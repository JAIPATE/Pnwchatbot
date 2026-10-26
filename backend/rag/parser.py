"""Document parsers for extracting structured content and metadata from HTML, PDF, and text documents."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from bs4 import BeautifulSoup
from pypdf import PdfReader


@dataclass
class ParsedSection:
    """Represents a discrete section within a document."""
    title: str
    content: str


@dataclass
class ParsedDocument:
    """Standardized representation of an ingested document."""
    doc_id: str
    title: str
    category: str
    source_url: str
    campus: str  # 'Hammond', 'Westville', or 'Both'
    file_type: str  # 'HTML', 'PDF', 'TEXT'
    sections: List[ParsedSection] = field(default_factory=list)
    raw_text: str = ""
    metadata: Dict = field(default_factory=dict)

    @property
    def full_content(self) -> str:
        """Returns concatenated text across all sections."""
        if self.sections:
            return "\n\n".join(f"## {s.title}\n{s.content}" for s in self.sections)
        return self.raw_text


class HTMLDocumentParser:
    """Parses HTML documents, extracting titles, metadata, and sections."""

    def parse(self, content_or_path: Union[str, Path], source_url: Optional[str] = None) -> ParsedDocument:
        if isinstance(content_or_path, Path) or (isinstance(content_or_path, str) and Path(content_or_path).is_file()):
            path = Path(content_or_path)
            html_text = path.read_text(encoding="utf-8")
            doc_id = path.stem
        else:
            html_text = content_or_path
            doc_id = "doc_" + str(abs(hash(html_text)) % 100000)

        soup = BeautifulSoup(html_text, "html.parser")

        # Strip scripts, styles, navigation
        for tag in soup(["script", "style", "nav", "noscript"]):
            tag.decompose()

        # Extract metadata
        meta_cat = soup.find("meta", attrs={"name": "category"})
        category = meta_cat["content"] if meta_cat and meta_cat.get("content") else "General Policy"

        meta_url = soup.find("meta", attrs={"name": "source-url"})
        url = source_url or (meta_url["content"] if meta_url and meta_url.get("content") else "https://www.pnw.edu")

        meta_campus = soup.find("meta", attrs={"name": "campus"})
        campus = meta_campus["content"] if meta_campus and meta_campus.get("content") else "Both"

        # Extract document title
        title_tag = soup.find("title")
        h1_tag = soup.find("h1")
        title = (
            title_tag.get_text(strip=True)
            if title_tag
            else (h1_tag.get_text(strip=True) if h1_tag else doc_id.replace("_", " ").title())
        )

        # Parse sections based on headings (h2, h3, or section tags)
        sections: List[ParsedSection] = []
        section_tags = soup.find_all("section")
        if section_tags:
            for sec in section_tags:
                heading = sec.find(["h2", "h3", "h4"])
                sec_title = heading.get_text(strip=True) if heading else "General"
                # Remove heading from text extraction
                body_text = " ".join(p.get_text(strip=True) for p in sec.find_all(["p", "ul", "ol", "li"]))
                if not body_text:
                    body_text = sec.get_text(separator=" ", strip=True)
                body_text = re.sub(r"\s+", " ", body_text).strip()
                if body_text:
                    sections.append(ParsedSection(title=sec_title, content=body_text))
        else:
            # Fallback: traverse headings
            current_title = "Overview"
            current_paragraphs: List[str] = []
            for elem in soup.find_all(["h2", "h3", "p", "li"]):
                if elem.name in ["h2", "h3"]:
                    if current_paragraphs:
                        sections.append(
                            ParsedSection(
                                title=current_title,
                                content=" ".join(current_paragraphs).strip(),
                            )
                        )
                        current_paragraphs = []
                    current_title = elem.get_text(strip=True)
                else:
                    text = elem.get_text(strip=True)
                    if text:
                        current_paragraphs.append(text)
            if current_paragraphs:
                sections.append(
                    ParsedSection(
                        title=current_title,
                        content=" ".join(current_paragraphs).strip(),
                    )
                )

        full_raw = soup.get_text(separator="\n", strip=True)

        return ParsedDocument(
            doc_id=doc_id,
            title=title,
            category=category,
            source_url=url,
            campus=campus,
            file_type="HTML",
            sections=sections,
            raw_text=full_raw,
            metadata={"parser": "HTMLDocumentParser"},
        )


class PDFDocumentParser:
    """Parses PDF documents using pypdf, extracting text and structural metadata."""

    def parse(self, file_path: Union[str, Path], source_url: Optional[str] = None) -> ParsedDocument:
        path = Path(file_path)
        reader = PdfReader(str(path))
        doc_id = path.stem

        page_texts: List[str] = []
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text() or ""
            if extracted.strip():
                page_texts.append(extracted.strip())

        full_text = "\n\n".join(page_texts)

        # Infer title from first line or PDF metadata
        pdf_title = reader.metadata.title if reader.metadata and reader.metadata.title else None
        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        title = pdf_title or (lines[0] if lines else doc_id.replace("_", " ").title())

        # Determine campus heuristic
        campus = "Both"
        if "hammond" in full_text.lower() and "westville" not in full_text.lower():
            campus = "Hammond"
        elif "westville" in full_text.lower() and "hammond" not in full_text.lower():
            campus = "Westville"

        # Split into logical sections by numbers/headings
        sections: List[ParsedSection] = []
        current_title = "Overview"
        current_block: List[str] = []

        heading_pattern = re.compile(r"^(\d+\.|\bSection\b|\bArticle\b|[A-Z\s]{4,}:)", re.IGNORECASE)

        for line in lines[1:]:
            if heading_pattern.match(line) or (len(line) < 60 and line.endswith(":")):
                if current_block:
                    sections.append(
                        ParsedSection(
                            title=current_title,
                            content=" ".join(current_block).strip(),
                        )
                    )
                    current_block = []
                current_title = line.rstrip(":")
            else:
                current_block.append(line)

        if current_block:
            sections.append(
                ParsedSection(
                    title=current_title,
                    content=" ".join(current_block).strip(),
                )
            )

        if not sections and full_text:
            sections.append(ParsedSection(title="Main Content", content=full_text))

        return ParsedDocument(
            doc_id=doc_id,
            title=title,
            category="University Policy",
            source_url=source_url or f"https://www.pnw.edu/policies/{path.name}",
            campus=campus,
            file_type="PDF",
            sections=sections,
            raw_text=full_text,
            metadata={"pages": len(reader.pages), "parser": "PDFDocumentParser"},
        )


class UniversalParser:
    """Universal dispatcher that parses any supported document format."""

    def __init__(self):
        self.html_parser = HTMLDocumentParser()
        self.pdf_parser = PDFDocumentParser()

    def parse_file(self, file_path: Union[str, Path], source_url: Optional[str] = None) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower()
        if ext in [".html", ".htm"]:
            return self.html_parser.parse(path, source_url=source_url)
        elif ext == ".pdf":
            return self.pdf_parser.parse(path, source_url=source_url)
        elif ext in [".txt", ".md"]:
            text = path.read_text(encoding="utf-8")
            return ParsedDocument(
                doc_id=path.stem,
                title=path.stem.replace("_", " ").title(),
                category="General",
                source_url=source_url or "https://www.pnw.edu",
                campus="Both",
                file_type="TEXT",
                sections=[ParsedSection(title="General", content=text)],
                raw_text=text,
                metadata={"parser": "TextParser"},
            )
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def parse_directory(self, dir_path: Union[str, Path]) -> List[ParsedDocument]:
        directory = Path(dir_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        results: List[ParsedDocument] = []
        for file in sorted(directory.iterdir()):
            if file.suffix.lower() in [".html", ".htm", ".pdf", ".txt", ".md"]:
                results.append(self.parse_file(file))
        return results
