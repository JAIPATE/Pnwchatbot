const fs = require('fs');
const path = require('path');

class PNWRAGEngine {
  constructor(corpusPath) {
    const rawData = fs.readFileSync(corpusPath, 'utf8');
    this.data = JSON.parse(rawData);
    this.documents = this.data.documents;
    this.departmentContacts = this.data.department_contacts;
  }

  /**
   * Process a student query with strict grounding and fail-safe policy.
   * @param {string} query User query text
   * @param {string} selectedCampus Filter scope ('All', 'Hammond', 'Westville')
   * @returns {Object} Structured RAG response
   */
  processQuery(query, selectedCampus = 'All') {
    const qLower = query.toLowerCase().trim();

    // 1. Detect West Lafayette or Non-PNW cross-campus confusion
    if (this.isWestLafayetteQuery(qLower)) {
      return this.buildCrossCampusFailSafeResponse(query, selectedCampus);
    }

    // 2. Score corpus documents based on term matching and semantic intent
    const scoredDocs = this.documents.map(doc => {
      let score = 0;
      const textToSearch = (doc.title + " " + doc.category + " " + doc.summary + " " + doc.content).toLowerCase();

      // Check campus filter compatibility
      if (selectedCampus !== 'All' && doc.campus !== 'Both' && doc.campus !== selectedCampus) {
        return { doc, score: -1 };
      }

      // Keyword & Phrase matching rules
      const keywords = this.extractKeywords(qLower);
      keywords.forEach(kw => {
        if (textToSearch.includes(kw)) {
          score += (doc.title.toLowerCase().includes(kw) ? 4 : 2);
        }
      });

      // Special Intent Boosters
      if (qLower.includes('park') || qLower.includes('ticket') || qLower.includes('citation') || qLower.includes('fine')) {
        if (doc.id === 'DOC-PARK-01') score += 10;
      }
      if (qLower.includes('dean') || qLower.includes('sul') || qLower.includes('lsf') || qLower.includes('office location') || qLower.includes('advocacy')) {
        if (doc.id === 'DOC-DOS-01') score += 10;
      }
      if (qLower.includes('plan of study') || qLower.includes('epos') || qLower.includes('cs ms') || qLower.includes('computer science ms')) {
        if (doc.id === 'DOC-CS-EPOS-01') score += 10;
      }
      if (qLower.includes('pin') || qLower.includes('add') || qLower.includes('drop') || qLower.includes('deadline') || qLower.includes('hold')) {
        if (doc.id === 'DOC-REG-01') score += 10;
      }
      if (qLower.includes('appeal') || qLower.includes('probation') || qLower.includes('gpa') || qLower.includes('grade')) {
        if (doc.id === 'DOC-APPEAL-01') score += 10;
      }

      return { doc, score };
    }).filter(item => item.score > 0);

    // Sort by score descending
    scoredDocs.sort((a, b) => b.score - a.score);

    // 3. Fail-Safe Trigger: If top score is below confidence threshold
    const CONFIDENCE_THRESHOLD = 3;
    if (scoredDocs.length === 0 || scoredDocs[0].score < CONFIDENCE_THRESHOLD) {
      return this.buildFailSafeResponse(query, selectedCampus, "No grounded policy document matching this specific request was found in official PNW documentation.");
    }

    // 4. Grounded Answer Construction
    const bestDoc = scoredDocs[0].doc;
    const answer = this.generateGroundedAnswer(qLower, bestDoc, selectedCampus);

    return {
      status: 'grounded_success',
      confidenceScore: Math.min(100, bestDoc.id ? (scoredDocs[0].score * 8 + 20) : 85),
      isGrounded: true,
      query: query,
      campusContext: bestDoc.campus === 'Both' ? 'Applicable to Hammond & Westville' : `${bestDoc.campus} Campus`,
      matchedDocument: {
        id: bestDoc.id,
        title: bestDoc.title,
        category: bestDoc.category,
        url: bestDoc.url
      },
      citationUrl: bestDoc.url,
      citationTitle: bestDoc.title,
      answerText: answer,
      departmentContacts: this.getRelevantContacts(qLower, selectedCampus)
    };
  }

  isWestLafayetteQuery(q) {
    const wlTerms = ['west lafayette', 'purdue wl', 'grant street garage', 'wl campus', 'phd in computer science', 'co-op wl'];
    return wlTerms.some(term => q.includes(term));
  }

  extractKeywords(q) {
    const stopWords = new Set(['how', 'do', 'i', 'can', 'the', 'a', 'an', 'what', 'is', 'where', 'are', 'to', 'for', 'my', 'in', 'at', 'on', 'of']);
    return q.split(/\W+/).filter(w => w.length > 2 && !stopWords.has(w));
  }

  generateGroundedAnswer(q, doc, campus) {
    let answer = "";

    if (doc.id === 'DOC-PARK-01') {
      answer = `### 🅿️ PNW Parking Citations & Regulations

To pay or appeal a parking citation at Purdue University Northwest (Hammond or Westville):

1. **Access the Portal**: Visit the official [PNW Parking Regulations Portal](${doc.url}).
2. **Log In**: Authenticate using your **myPNW credentials**.
3. **Submit within 14 Days**: Citations must be resolved or appealed within **14 calendar days** to avoid a Registrar account hold.
4. **Virtual Permits**: Ensure your vehicle license plate is registered accurately in the portal before parking in student lots.

> **Campus Notice**: PNW parking permits and citations are managed independently from Purdue West Lafayette. Passes from West Lafayette are not valid at PNW Hammond or Westville campuses.`;
    } else if (doc.id === 'DOC-DOS-01') {
      const showHammond = campus === 'All' || campus === 'Hammond';
      const showWestville = campus === 'All' || campus === 'Westville';

      answer = `### 🏢 Office of the Dean of Students Locations

The Office of the Dean of Students provides student advocacy, academic grievance guidance, and emergency support.

${showHammond ? `**Hammond Campus Location:**
- **Office**: Student Union & Library Building (SUL), Room 313
- **Phone**: (219) 989-2367
- **Email**: [dos@pnw.edu](mailto:dos@pnw.edu)
- **Hours**: Mon - Fri, 8:00 AM - 5:00 PM CST\n\n` : ''}${showWestville ? `**Westville Campus Location:**
- **Office**: Library-Student Faculty Building (LSF), Room 103
- **Phone**: (219) 785-5551
- **Email**: [dos@pnw.edu](mailto:dos@pnw.edu)
- **Hours**: Mon - Fri, 8:00 AM - 4:30 PM CST\n\n` : ''}For additional policy details, visit the official [PNW Dean of Students Webpage](${doc.url}).`;
    } else if (doc.id === 'DOC-CS-EPOS-01') {
      answer = `### 🎓 MS in Computer Science Electronic Plan of Study (EPOS) Guide

To submit your Plan of Study for the Computer Science MS program at PNW:

1. **Log in to myPNW Portal**: Access [myPNW](https://mypnw.pnw.edu) and select the **Graduate School Plan of Study** tab.
2. **Create Draft**: Click **Create New Plan of Study** and set your degree objective to **Computer Science MS**.
3. **Assign Advisor**: Designate your primary Academic Advisor as the Advisory Committee Chair.
4. **Add Course Credits**: Include 30 required graduate credits (Core CS courses and approved electives).
5. **Submit for Approval**: Submit your draft.

⚠️ **Mandatory Requirement**: Your Academic Advisor **must digitally approve** your EPOS before it becomes active. Any course substitutions require prior advisor consultation.

Source: [PNW Graduate Computer Science Programs](${doc.url})`;
    } else if (doc.id === 'DOC-REG-01') {
      answer = `### 📋 Registration PINs, Add/Drop Deadlines & Holds

**1. How to get your Registration PIN:**
- All PNW degree-seeking students require an advisor-cleared PIN each semester.
- **PINs are NOT given out via automated helpdesks**. You must schedule an advising appointment with your assigned Academic Advisor, who will issue your PIN after approving your schedule.

**2. Add/Drop Deadlines:**
- **Week 1**: Add or drop classes in myPNW with no financial/academic penalty.
- **Weeks 2–9**: Dropping a class registers a '**W**' (Withdrawal) on your official transcript.
- **After Week 9**: Requires formal authorization from the College Dean and Dean of Students.

**3. Student Account Holds:**
- Check hold details in myPNW. Holds must be resolved with the respective department (Bursar for unpaid fees, Registrar for transcripts, Parking for citations).

Source: [PNW Academic & Registration Regulations](${doc.url})`;
    } else if (doc.id === 'DOC-APPEAL-01') {
      answer = `### ⚖️ Grade Appeals & Academic Standing Policy

**Step-by-step Grade Appeal Process:**
1. **Informal Discussion**: Contact your course instructor within **30 calendar days** of final grade posting to request a review.
2. **Departmental Appeal**: If unresolved, file a written statement with the Department Head detailing evidence of arbitrary/capricious grading.
3. **Formal Committee Appeal**: If necessary, submit a formal petition through the Dean of Students office.

**Academic Standing Thresholds:**
- **Undergraduate**: Cumulative GPA below 2.00 places student on Academic Probation.
- **Graduate**: Minimum 3.00 Cumulative GPA required for good academic standing.

Source: [PNW Grade Appeals & Regulations](${doc.url})`;
    } else {
      answer = `### ${doc.title}\n\n${doc.content}\n\nSource: [${doc.title}](${doc.url})`;
    }

    return answer;
  }

  buildCrossCampusFailSafeResponse(query, campus) {
    return {
      status: 'failsafe_cross_campus',
      confidenceScore: 0,
      isGrounded: false,
      query: query,
      campusContext: 'Cross-Campus Flagged',
      answerText: `### ⚠️ Policy Mismatch / Fail-Safe Notice

Your query mentions rules or locations associated with **Purdue University West Lafayette** (e.g., West Lafayette parking garages, West Lafayette campus housing, or WL PhD programs).

**Purdue Northwest (PNW)** operates under distinct administrative policies, registration systems, and parking portals.

If you are a PNW student seeking assistance, please rephrase your query for **PNW Hammond** or **PNW Westville**, or contact the Dean of Students office for guidance.`,
      citationUrl: "https://www.pnw.edu/dean-of-students/",
      citationTitle: "PNW Dean of Students Office",
      departmentContacts: this.getRelevantContacts(query, campus)
    };
  }

  buildFailSafeResponse(query, campus, reason) {
    return {
      status: 'failsafe_ungrounded',
      confidenceScore: 0,
      isGrounded: false,
      query: query,
      campusContext: campus === 'All' ? 'Hammond & Westville' : `${campus} Campus`,
      answerText: `### ℹ️ Fail-Safe Response: Unsupported Query

**I am unable to provide a reliable answer to this question.**

*Reason*: ${reason}

To ensure you receive 100% accurate official information without risk of incorrect policy details, please contact the appropriate PNW University Department directly using the contact cards below.`,
      citationUrl: "https://www.pnw.edu/dean-of-students/",
      citationTitle: "PNW Department Directory",
      departmentContacts: this.getRelevantContacts(query, campus)
    };
  }

  getRelevantContacts(q, campus) {
    let filtered = this.departmentContacts;
    if (campus !== 'All') {
      filtered = filtered.filter(c => c.campus === 'Both' || c.campus === campus);
    }
    return filtered;
  }

  getAllCorpus() {
    return this.data;
  }
}

module.exports = PNWRAGEngine;
