// ============================================================
// PNW Knowledge Chatbot & Student Portal Application Logic
// ============================================================

let activeCampusId = 1;
let activeCampusName = "Hammond Campus";
let currentSessionId = "session-" + Math.random().toString(36).substring(2, 9);

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initCampusModal();
    loadScheduleTable();
    loadPrerequisites();
    loadCorpusDocs();
});

// Tab Navigation
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            navButtons.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
            
            btn.classList.add("active");
            const targetTab = btn.getAttribute("data-tab");
            document.getElementById(targetTab).classList.add("active");
        });
    });
}

// Campus Modal
function initCampusModal() {
    const modalBtn = document.getElementById("campusSelectorBtn");
    modalBtn.addEventListener("click", () => {
        document.getElementById("campusModal").classList.add("active");
    });
}

function closeCampusModal() {
    document.getElementById("campusModal").classList.remove("active");
}

function selectCampus(id, name) {
    activeCampusId = id;
    activeCampusName = name;
    document.getElementById("currentCampusLabel").innerText = name;
    
    document.querySelectorAll(".campus-card").forEach((card, idx) => {
        if ((idx + 1) === id) card.classList.add("active");
        else card.classList.remove("active");
    });
}

// Chat Submission & SSE Streaming
function sendPrompt(text) {
    document.getElementById("chatInput").value = text;
    handleChatSubmit(new Event("submit"));
}

async function handleChatSubmit(e) {
    if (e) e.preventDefault();
    const inputEl = document.getElementById("chatInput");
    const query = inputEl.value.strip ? inputEl.value.strip() : inputEl.value.trim();
    
    if (!query) return;
    inputEl.value = "";

    const chatMessages = document.getElementById("chatMessages");

    // Append User Message
    const userMsgDiv = document.createElement("div");
    userMsgDiv.className = "message user-message";
    userMsgDiv.innerHTML = `
        <div class="avatar">👤</div>
        <div class="message-content"><p>${escapeHtml(query)}</p></div>
    `;
    chatMessages.appendChild(userMsgDiv);

    // Append Assistant Message Placeholder
    const assistantMsgDiv = document.createElement("div");
    assistantMsgDiv.className = "message assistant-message";
    assistantMsgDiv.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message-content"><p id="currentStreamText"><span class="typing">...</span></p></div>
    `;
    chatMessages.appendChild(assistantMsgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const streamTextEl = assistantMsgDiv.querySelector("#currentStreamText");
    streamTextEl.innerText = "";

    try {
        const response = await fetch("/api/chat/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                campus_id: activeCampusId,
                session_id: currentSessionId
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split("\n\n");
            buffer = events.pop(); // Keep last incomplete event in buffer

            for (const eventStr of events) {
                if (!eventStr.trim()) continue;
                const lines = eventStr.split("\n");
                let eventType = "";
                let dataText = "";

                for (const line of lines) {
                    if (line.startsWith("event: ")) eventType = line.substring(7).trim();
                    if (line.startsWith("data: ")) dataText = line.substring(6).trim();
                }

                if (eventType === "metadata") {
                    const meta = JSON.parse(dataText);
                    renderCitations(meta.citations);
                } else if (eventType === "token") {
                    const tokenObj = JSON.parse(dataText);
                    streamTextEl.innerText += tokenObj.token;
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }
        }
    } catch (err) {
        streamTextEl.innerText = "Error connecting to chatbot server. Please check backend status.";
    }
}

function renderCitations(citations) {
    const container = document.getElementById("citationsContainer");
    if (!citations || citations.length === 0) {
        container.innerHTML = `
            <div class="empty-citations">
                <span>🛡️</span>
                <p>No official source citations matched. Response triggered Fail-Safe Policy.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = citations.map(c => `
        <div class="citation-card">
            <strong>📖 ${escapeHtml(c.document_title)}</strong>
            <div><small>${escapeHtml(c.section_title)}</small></div>
            <a href="${c.source_url}" target="_blank">View Source Document ➔</a>
        </div>
    `).join("");
}

// Academic Schedule Table Loading
async function loadScheduleTable() {
    const term = document.getElementById("termSelect").value;
    const url = term ? `/api/schedule?term=${term}` : "/api/schedule";
    
    try {
        const res = await fetch(url);
        const data = await res.json();
        const tbody = document.getElementById("scheduleTableBody");

        tbody.innerHTML = data.map(item => `
            <tr>
                <td><strong>${escapeHtml(item.term)}</strong></td>
                <td>${escapeHtml(item.event_name)}</td>
                <td>📅 ${item.deadline_date}</td>
                <td><strong style="color:var(--gold-bright)">${item.refund_percentage}%</strong></td>
                <td>${escapeHtml(item.notes || '-')}</td>
                <td>
                    ${item.is_expired ? 
                        '<span class="badge-expired">Past Deadline</span>' : 
                        '<span class="badge-active">Upcoming</span>'}
                </td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Failed to load schedule", err);
    }
}

// Prerequisite Graph Loading
async function loadPrerequisites() {
    const courseCode = document.getElementById("courseSelect").value;
    try {
        const res = await fetch(`/api/prerequisites?course_code=${encodeURIComponent(courseCode)}`);
        const data = await res.json();

        const canvas = document.getElementById("graphCanvas");
        const details = document.getElementById("prereqSummaryContent");

        if (!data.prerequisites || data.prerequisites.length === 0) {
            canvas.innerHTML = `<div class="tree-node">${escapeHtml(courseCode)}<br><small>No Prerequisites Required</small></div>`;
            details.innerHTML = `<p><strong>${escapeHtml(courseCode)}</strong> can be taken without prior CS prerequisites.</p>`;
            return;
        }

        // Render visual tree nodes
        canvas.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; gap:1.5rem">
                <div style="display:flex; gap:1rem">
                    ${data.prerequisites.map(p => `
                        <div class="tree-node" style="background:rgba(56, 189, 248, 0.15); border-color:var(--accent-blue)">
                            ${escapeHtml(p.prerequisite_code)}
                            <br><small>Min Grade: ${p.minimum_grade}</small>
                        </div>
                    `).join("")}
                </div>
                <div style="font-size:1.5rem; color:var(--gold-bright)">⬇ REQUIRED FOR ⬇</div>
                <div class="tree-node">${escapeHtml(data.target_course)}</div>
            </div>
        `;

        details.innerHTML = `
            <p>To register for <strong>${escapeHtml(data.target_course)}</strong>, you must complete:</p>
            <ul style="margin-left:1.2rem; margin-top:0.5rem">
                ${data.prerequisites.map(p => `
                    <li><strong>${p.prerequisite_code}</strong> (${p.course_title}) with grade <strong>${p.minimum_grade} or higher</strong>. Availability: <em>${p.campus_availability}</em></li>
                `).join("")}
            </ul>
        `;
    } catch (err) {
        console.error("Failed to load prerequisites", err);
    }
}

// Corpus Documents Cards
async function loadCorpusDocs() {
    const docs = [
        { title: "PNW Parking Regulations & Fees", category: "Parking Policy", url: "https://www.pnw.edu/getting-to-pnw/parking-and-fees/regulations-and-enforcement/" },
        { title: "PNW Academic Schedule & Refund Policy", category: "Academic Schedule", url: "https://www.pnw.edu/registrar/academic-schedule/" },
        { title: "PNW Academic Catalog & CS Prereqs", category: "Catalog", url: "https://catalog.pnw.edu/preview_program.php?catoid=5&poid=1338&returnto=271" },
        { title: "PNW Student Handbook 2024-2025", category: "Student PDF Handbook", url: "https://www.pnw.edu/concurrent-enrollment/wp-content/uploads/sites/4/2020/02/STUDENT-HANDBOOK.pdf" },
        { title: "PNW Classroom Behavior Policy", category: "Senate Policy PDF", url: "https://www.pnw.edu/faculty-senate/wp-content/uploads/sites/71/2021/01/Classroom-Behavior-Policy.pdf" },
        { title: "PNW Graduate School & POS Policy", category: "Graduate School", url: "https://catalog.pnw.edu/content.php?catoid=4&navoid=154#admission-to-the-graduate-school" }
    ];

    const grid = document.getElementById("docCardsGrid");
    grid.innerHTML = docs.map(d => `
        <div class="citation-card" style="padding:1.2rem">
            <span class="badge-active" style="margin-bottom:0.5rem; display:inline-block">${d.category}</span>
            <h3 style="color:#fff; font-size:1.05rem">${d.title}</h3>
            <a href="${d.url}" target="_blank" style="margin-top:0.8rem; display:inline-block">Open Official Source ➔</a>
        </div>
    `).join("");
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
