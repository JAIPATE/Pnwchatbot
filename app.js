document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const chatForm = document.getElementById('chatForm');
  const userInput = document.getElementById('userInput');
  const chatMessages = document.getElementById('chatMessages');
  const typingIndicator = document.getElementById('typingIndicator');
  const campusSelect = document.getElementById('campusSelect');
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const latencyMetric = document.getElementById('latencyMetric');
  const activeScopeLabel = document.getElementById('activeScopeLabel');

  // Navigation Buttons & View Panels
  const navBtns = document.querySelectorAll('.nav-btn');
  const viewPanels = document.querySelectorAll('.view-panel');
  const corpusListContainer = document.getElementById('corpusListContainer');
  const contactsListContainer = document.getElementById('contactsListContainer');

  // State
  let selectedCampus = 'All';

  // --- 1. Tab Navigation Handler ---
  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.getAttribute('data-tab');
      
      navBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      viewPanels.forEach(panel => {
        if (panel.id === `${tabName}View`) {
          panel.style.display = 'flex';
          panel.classList.add('active');
        } else {
          panel.style.display = 'none';
          panel.classList.remove('active');
        }
      });

      if (tabName === 'corpus') fetchCorpusData();
      if (tabName === 'contacts') fetchContactsData();
    });
  });

  // --- 2. Campus Filter Change ---
  campusSelect.addEventListener('change', (e) => {
    selectedCampus = e.target.value;
    activeScopeLabel.textContent = selectedCampus === 'All' ? 'Hammond & Westville' : `${selectedCampus} Campus`;
  });

  // --- 3. Quick Prompt Chips Click Handler ---
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      userInput.value = query;
      handleUserSubmit(query);
    });
  });

  // --- 4. Form Submit Handler ---
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;
    handleUserSubmit(query);
  });

  async function handleUserSubmit(query) {
    userInput.value = '';

    // Append User Message Card
    appendUserMessage(query);

    // Show Typing Indicator
    showTyping(true);

    const startTime = performance.now();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, campus: selectedCampus })
      });

      const data = await response.json();
      const endTime = performance.now();
      const latency = Math.round(endTime - startTime);
      latencyMetric.textContent = `${latency} ms`;

      showTyping(false);

      // Append Bot Response Card
      appendBotMessage(data);

    } catch (err) {
      showTyping(false);
      appendBotMessage({
        status: 'failsafe_ungrounded',
        isGrounded: false,
        confidenceScore: 0,
        answerText: '### ⚠️ Network Error\n\nUnable to connect to the PNW Chatbot backend. Please check your connection and try again.',
        departmentContacts: []
      });
    }
  }

  // --- 5. Message Renderers ---
  function appendUserMessage(text) {
    const card = document.createElement('div');
    card.className = 'message-card user-message';
    card.innerHTML = `
      <div class="avatar user-avatar"><i class="fa-solid fa-user"></i></div>
      <div class="message-body">
        <div class="message-header">
          <span class="sender-name">You</span>
          <span class="timestamp">${getCurrentTime()}</span>
        </div>
        <div class="message-text"><p>${escapeHtml(text)}</p></div>
      </div>
    `;
    chatMessages.appendChild(card);
    scrollToBottom();
  }

  function appendBotMessage(data) {
    const card = document.createElement('div');
    const isFailsafe = !data.isGrounded;
    card.className = `message-card bot-message ${isFailsafe ? 'failsafe-message' : ''}`;

    const parsedMarkdown = renderMarkdown(data.answerText);

    let contactsHtml = '';
    if (isFailsafe && data.departmentContacts && data.departmentContacts.length > 0) {
      contactsHtml = `
        <div class="contacts-grid-mini">
          ${data.departmentContacts.map(c => `
            <div class="contact-card-mini">
              <h4><i class="fa-solid fa-building"></i> ${escapeHtml(c.department)}</h4>
              <p><i class="fa-solid fa-location-dot"></i> ${escapeHtml(c.location)}</p>
              <p><i class="fa-solid fa-phone"></i> ${escapeHtml(c.phone)} | <i class="fa-solid fa-envelope"></i> <a href="mailto:${escapeHtml(c.email)}">${escapeHtml(c.email)}</a></p>
            </div>
          `).join('')}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="avatar bot-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="message-body">
        <div class="message-header">
          <span class="sender-name">PNW Knowledge Bot</span>
          ${data.isGrounded 
            ? `<span class="badge badge-grounded"><i class="fa-solid fa-circle-check"></i> ${data.confidenceScore}% Grounded (${data.campusContext})</span>`
            : `<span class="badge badge-failsafe"><i class="fa-solid fa-shield-cat"></i> Fail-Safe Triggered (${data.campusContext})</span>`
          }
          <span class="timestamp">${getCurrentTime()}</span>
        </div>
        <div class="message-text">
          ${parsedMarkdown}
          ${contactsHtml}
        </div>
        <div class="message-actions">
          <span>${data.matchedDocument ? `Source: ${escapeHtml(data.matchedDocument.title)}` : 'PNW Policy Engine'}</span>
          <div class="action-btn-group">
            <button class="action-icon-btn copy-btn" title="Copy Response"><i class="fa-solid fa-copy"></i></button>
            <button class="action-icon-btn feedback-btn" title="Helpful"><i class="fa-regular fa-thumbs-up"></i></button>
            <button class="action-icon-btn feedback-btn" title="Not Helpful"><i class="fa-regular fa-thumbs-down"></i></button>
          </div>
        </div>
      </div>
    `;

    chatMessages.appendChild(card);
    scrollToBottom();

    // Copy Listener
    card.querySelector('.copy-btn').addEventListener('click', (e) => {
      navigator.clipboard.writeText(data.answerText);
      const icon = e.currentTarget.querySelector('i');
      icon.className = 'fa-solid fa-check';
      setTimeout(() => { icon.className = 'fa-solid fa-copy'; }, 1500);
    });

    // Feedback Listeners
    card.querySelectorAll('.feedback-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const icon = e.currentTarget.querySelector('i');
        if (icon.classList.contains('fa-regular')) {
          icon.classList.replace('fa-regular', 'fa-solid');
          e.currentTarget.style.color = '#34D399';
        }
      });
    });
  }

  function showTyping(visible) {
    typingIndicator.style.display = visible ? 'flex' : 'none';
    if (visible) scrollToBottom();
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // --- 6. Markdown Renderer ---
  function renderMarkdown(mdText) {
    if (!mdText) return '';
    let html = mdText
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1 <i class="fa-solid fa-arrow-up-right-from-square"></i></a>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
    
    return html.replace(/\n\n/g, '<br/>');
  }

  // --- 7. Voice Query Simulation ---
  voiceToggleBtn.addEventListener('click', () => {
    const sampleQueries = [
      "How do I pay parking citations at Hammond?",
      "Where is the Office of the Dean of Students?",
      "How do I submit Computer Science MS EPOS?",
      "What are the add/drop deadlines for classes?"
    ];
    const picked = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];
    
    userInput.value = "";
    let i = 0;
    const timer = setInterval(() => {
      userInput.value += picked.charAt(i);
      i++;
      if (i >= picked.length) {
        clearInterval(timer);
      }
    }, 40);
  });

  // --- 8. Clear History ---
  clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = `
      <div class="message-card bot-message welcome-card">
        <div class="avatar bot-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="message-body">
          <div class="message-header">
            <span class="sender-name">PNW Assistant</span>
            <span class="badge badge-grounded"><i class="fa-solid fa-shield-halved"></i> Grounded</span>
          </div>
          <div class="message-text">
            <p>Chat history cleared. How can I assist you with Purdue Northwest policies today?</p>
          </div>
        </div>
      </div>
    `;
  });

  // --- 9. Fetch Corpus & Contacts Data ---
  async function fetchCorpusData() {
    try {
      const res = await fetch('/api/corpus');
      const data = await res.json();
      corpusListContainer.innerHTML = data.documents.map(doc => `
        <div class="doc-card">
          <div>
            <div class="doc-card-header">
              <span class="doc-id">${escapeHtml(doc.id)}</span>
              <span class="badge badge-grounded">${escapeHtml(doc.campus)} Campus</span>
            </div>
            <h3>${escapeHtml(doc.title)}</h3>
            <p>${escapeHtml(doc.summary)}</p>
          </div>
          <a href="${escapeHtml(doc.url)}" target="_blank" class="doc-link">
            Official Source Webpage <i class="fa-solid fa-external-link"></i>
          </a>
        </div>
      `).join('');
    } catch (e) {
      corpusListContainer.innerHTML = '<p>Unable to load knowledge corpus.</p>';
    }
  }

  async function fetchContactsData() {
    try {
      const res = await fetch('/api/corpus');
      const data = await res.json();
      contactsListContainer.innerHTML = data.department_contacts.map(c => `
        <div class="contact-card">
          <div class="contact-card-header">
            <h3 style="color: var(--pnw-gold); font-size: 16px;"><i class="fa-solid fa-building-user"></i> ${escapeHtml(c.department)}</h3>
            <span class="badge badge-grounded">${escapeHtml(c.campus)}</span>
          </div>
          <p style="margin: 10px 0;"><i class="fa-solid fa-location-dot" style="color: var(--accent-blue);"></i> <strong>Location:</strong> ${escapeHtml(c.location)}</p>
          <p style="margin-bottom: 6px;"><i class="fa-solid fa-phone"></i> <strong>Phone:</strong> ${escapeHtml(c.phone)}</p>
          <p style="margin-bottom: 6px;"><i class="fa-solid fa-envelope"></i> <strong>Email:</strong> <a href="mailto:${escapeHtml(c.email)}">${escapeHtml(c.email)}</a></p>
          <p style="font-size: 12px; color: var(--text-muted);"><i class="fa-solid fa-clock"></i> <strong>Hours:</strong> ${escapeHtml(c.hours)}</p>
        </div>
      `).join('');
    } catch (e) {
      contactsListContainer.innerHTML = '<p>Unable to load contacts directory.</p>';
    }
  }

  // Utilities
  function getCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
});
