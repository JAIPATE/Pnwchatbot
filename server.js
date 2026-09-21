const express = require('express');
const cors = require('cors');
const path = require('path');
const PNWRAGEngine = require('./src/rag_engine');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Initialize RAG Engine
const corpusPath = path.join(__dirname, 'src', 'data', 'pnw_corpus.json');
const ragEngine = new PNWRAGEngine(corpusPath);

// API Endpoints
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    institution: 'Purdue University Northwest',
    version: '2026.1',
    groundedEngine: 'Active',
    constitutionPrinciples: ['100% Grounded Answers', 'Fail-Safe Routing', 'Campus Disambiguation']
  });
});

app.post('/api/chat', (req, res) => {
  const { query, campus } = req.body;
  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  const response = ragEngine.processQuery(query, campus || 'All');
  res.json(response);
});

app.get('/api/corpus', (req, res) => {
  res.json(ragEngine.getAllCorpus());
});

// Fallback to index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Start Server
app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`🚀 PNW Knowledge Chatbot Server is running live!`);
  console.log(`📍 URL: http://localhost:${PORT}`);
  console.log(`🛡️  Grounded Policy Engine: Active (Corpus v2026.1)`);
  console.log(`====================================================`);
});
