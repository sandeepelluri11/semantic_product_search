## AI-Powered Semantic Search & Product Ranking System

This project is a full-stack prototype of an AI-powered semantic product search and ranking system, similar to the one described on your resume.

### Tech stack
- **Backend**: Python, FastAPI, Elasticsearch
- **Frontend**: React (Vite)

### Features
- **Semantic search API** that queries Elasticsearch.
- **ML-style ranking pipeline** that scores products by textual relevance, popularity, and user behavior signals.
- **React UI** for real-time search and result exploration.

### Getting started

#### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`.

#### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173` by default and talk to the backend on `http://localhost:8000`.

