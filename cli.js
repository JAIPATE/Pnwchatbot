const readline = require('readline');
const path = require('path');
const PNWRAGEngine = require('./src/rag_engine');

// ANSI Color Codes for Terminal Output
const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  gold: '\x1b[38;2;229;168;35m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  gray: '\x1b[90m',
  white: '\x1b[37m'
};

// Initialize RAG Engine
const corpusPath = path.join(__dirname, 'src', 'data', 'pnw_corpus.json');
const ragEngine = new PNWRAGEngine(corpusPath);

let currentCampus = 'All';

// Create Readline Interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: `${colors.gold}${colors.bold}PNW Student Query> ${colors.reset}`
});

function printBanner() {
  console.clear();
  console.log(`${colors.gold}${colors.bold}=====================================================================${colors.reset}`);
  console.log(`${colors.gold}${colors.bold}  🎓 PURDUE UNIVERSITY NORTHWEST (PNW) KNOWLEDGE CHATBOT [CMD MODE]  ${colors.reset}`);
  console.log(`${colors.gold}${colors.bold}=====================================================================${colors.reset}`);
  console.log(`${colors.gray}100% Grounded Policy Engine & Fail-Safe Department Routing Active${colors.reset}`);
  console.log(`${colors.cyan}Current Campus Scope: ${colors.bold}${currentCampus}${colors.reset}\n`);
  console.log(`${colors.white}Available Quick Commands:${colors.reset}`);
  console.log(`  ${colors.yellow}/campus [all|hammond|westville]${colors.reset} - Switch campus scope`);
  console.log(`  ${colors.yellow}/corpus${colors.reset}                         - View official PNW document list`);
  console.log(`  ${colors.yellow}/contacts${colors.reset}                       - View department contacts directory`);
  console.log(`  ${colors.yellow}/help${colors.reset}                           - Show help menu`);
  console.log(`  ${colors.yellow}/exit${colors.reset}                           - Exit chatbot CLI\n`);
  console.log(`${colors.gray}Type your question below (e.g., "How do I pay parking citations at Hammond?"):${colors.reset}\n`);
}

function formatMarkdownToAnsi(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, `${colors.gold}${colors.bold}=== $1 ===${colors.reset}`)
    .replace(/^## (.*$)/gim, `${colors.gold}${colors.bold}=== $1 ===${colors.reset}`)
    .replace(/^\> (.*$)/gim, `${colors.gray}│ $1${colors.reset}`)
    .replace(/\*\*(.*?)\*\*/g, `${colors.bold}$1${colors.reset}`)
    .replace(/\[(.*?)\]\((.*?)\)/g, `${colors.cyan}$1${colors.reset} (${colors.gray}$2${colors.reset})`);
}

function processCommandLine(line) {
  const input = line.trim();
  if (!input) {
    rl.prompt();
    return;
  }

  // Handle Commands
  if (input.startsWith('/')) {
    const parts = input.split(' ');
    const cmd = parts[0].toLowerCase();

    if (cmd === '/exit' || cmd === '/quit') {
      console.log(`\n${colors.gold}Thank you for using the PNW Knowledge Chatbot. Boiler Up! 🦁${colors.reset}\n`);
      process.exit(0);
    } else if (cmd === '/campus') {
      const scope = parts[1] ? parts[1].toLowerCase() : '';
      if (scope === 'hammond') currentCampus = 'Hammond';
      else if (scope === 'westville') currentCampus = 'Westville';
      else currentCampus = 'All';
      console.log(`\n${colors.green}✔ Campus scope updated to: ${colors.bold}${currentCampus}${colors.reset}\n`);
    } else if (cmd === '/corpus') {
      const docs = ragEngine.getAllCorpus().documents;
      console.log(`\n${colors.gold}${colors.bold}=== OFFICIAL PNW DOCUMENT CORPUS ===${colors.reset}`);
      docs.forEach(doc => {
        console.log(`\n${colors.cyan}[${doc.id}] ${doc.title}${colors.reset} (${colors.yellow}${doc.campus} Campus${colors.reset})`);
        console.log(`  ${colors.gray}URL:${colors.reset} ${doc.url}`);
        console.log(`  ${colors.gray}Summary:${colors.reset} ${doc.summary}`);
      });
      console.log('');
    } else if (cmd === '/contacts') {
      const contacts = ragEngine.getAllCorpus().department_contacts;
      console.log(`\n${colors.gold}${colors.bold}=== PNW DEPARTMENT CONTACT DIRECTORY ===${colors.reset}`);
      contacts.forEach(c => {
        console.log(`\n${colors.yellow}${colors.bold}• ${c.department}${colors.reset} (${c.campus} Campus)`);
        console.log(`  ${colors.gray}Location:${colors.reset} ${c.location}`);
        console.log(`  ${colors.gray}Phone:${colors.reset} ${c.phone} | ${colors.gray}Email:${colors.reset} ${c.email}`);
      });
      console.log('');
    } else if (cmd === '/help') {
      printBanner();
    } else {
      console.log(`\n${colors.red}Unknown command: ${cmd}. Type /help for options.${colors.reset}\n`);
    }

    rl.prompt();
    return;
  }

  // Handle Query
  console.log(`\n${colors.gray}Searching official PNW documentation...${colors.reset}\n`);
  const response = ragEngine.processQuery(input, currentCampus);

  if (response.isGrounded) {
    console.log(`${colors.green}${colors.bold}[GROUNDED ANSWER] (${response.confidenceScore}% Confidence - ${response.campusContext})${colors.reset}`);
    console.log(`---------------------------------------------------------------------`);
    console.log(formatMarkdownToAnsi(response.answerText));
    console.log(`---------------------------------------------------------------------`);
    console.log(`${colors.gray}Official Citation:${colors.reset} ${colors.cyan}${response.matchedDocument.title}${colors.reset} (${response.matchedDocument.url})\n`);
  } else {
    console.log(`${colors.red}${colors.bold}[FAIL-SAFE TRIGGERED] (${response.campusContext})${colors.reset}`);
    console.log(`---------------------------------------------------------------------`);
    console.log(formatMarkdownToAnsi(response.answerText));
    console.log(`---------------------------------------------------------------------\n`);

    if (response.departmentContacts && response.departmentContacts.length > 0) {
      console.log(`${colors.gold}${colors.bold}Recommended Department Contacts:${colors.reset}`);
      response.departmentContacts.slice(0, 3).forEach(c => {
        console.log(`  ${colors.bold}• ${c.department}:${colors.reset} ${c.location} | Phone: ${c.phone} | Email: ${c.email}`);
      });
      console.log('');
    }
  }

  rl.prompt();
}

// Start CLI
printBanner();
rl.prompt();

rl.on('line', (line) => {
  processCommandLine(line);
});
