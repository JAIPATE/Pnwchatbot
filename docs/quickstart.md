# Quickstart Guide (quickstart.md) - PNW Knowledge Chatbot

Follow these steps to run and validate the Purdue University Northwest Knowledge Chatbot system locally.

---

## 📋 Prerequisites
- **Python 3.11+** installed
- **Git** installed
- **Node.js 18+** (Optional, for frontend development)

---

## ⚡ Step 1: Clone & Setup Environment

```bash
# Clone repository
git clone <your-github-repo-url>
cd pnw-knowledge-chatbot

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 💾 Step 2: Initialize & Seed Database

Run the database seed script to execute DDL (`db/schema.sql`) and populate PNW document corpus, academic schedules, course prerequisites, and parking rules:

```bash
python db/seed_data.py
```

Expected Output:
```
[INFO] Database pnw_database.db schema created successfully.
[INFO] Seeded 2 campuses (Hammond, Westville).
[INFO] Seeded 8 corpus documents & 24 chunks.
[INFO] Seeded academic schedule deadlines & course prerequisites.
```

---

## 🚀 Step 3: Run FastAPI Application Backend

Start the FastAPI application server:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Access Points:
- **Web App Interface**: `http://localhost:8000`
- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 🧪 Step 4: Run Automated Tests

Execute automated unit and integration tests:

```bash
pytest tests/
```

---

## 🔍 Step 5: Manual Validation Checklist

1. **Campus Selection**: Open `http://localhost:8000`, select **Hammond Campus** or **Westville Campus**.
2. **Chatbot Policy Query**: Type *"How do I pay a parking ticket at PNW?"* -> Verify response includes official payment portal link and citation.
3. **Fail-Safe Test**: Type *"What is the recipe for chocolate chip cookies?"* -> Verify chatbot responds with fail-safe refusal ("I don't know / contact office").
4. **Academic Schedule**: Click **Academic Deadlines** tab -> Verify 100% refund date table is rendered without date scrambling.
5. **Prerequisites Graph**: Click **Prerequisites** tab -> Search `CS 30200` -> Verify visual node graph displays required prerequisites (`CS 18000`, `MA 16100`).
