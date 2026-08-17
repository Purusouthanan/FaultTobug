# Incident-to-Regression Automation Platform

A complete end-to-end AI platform that translates unstructured English bug reports (incidents) into executable, permanent regression tests for FastAPI applications.

## Overview

When an incident occurs in production, engineers usually have to manually read the report, reproduce the bug locally, and write a test to ensure it never happens again. This platform automates that entire process:
1. **Analyze**: Extracts the Role, Endpoint, and Expected Result from a natural language incident description.
2. **Reproduce**: Intelligently simulates API requests required to reproduce the bug based on the extracted information.
3. **Generate**: Converts those reproduction steps into executable Pytest Python code.
4. **Execute**: Runs the generated test dynamically in an isolated test database. 
5. **Guard**: Converts passing tests into a permanent Regression Test Suite.

## Architecture

The project consists of two main components:
- **Backend (FastAPI)**: The core AI engine. Manages the hospital simulator API, handles incident storage, interacts with the LLM (Gemini 2.5 Flash), and dynamically executes Pytest in a subprocess against an in-memory SQLite database.
- **Frontend (React)**: A beautiful, modern Vite-powered UI to view dashboards, manage incidents, and interact with the pipeline in real time.

## Quickstart

### Prerequisites
- Python 3.12+
- Node.js & npm
- Gemini API Key

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory with:
```env
GEMINI_API_KEY=your_api_key_here
```
Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The UI will be accessible at `http://localhost:5173`.

## Demonstration
You can see an automated End-to-End demonstration of the platform converting a security bug into a passing regression test by running:
```bash
cd backend
python scripts/e2e_demo_part1.py
# Fix the bug in backend/app/routers/patients.py
python scripts/e2e_demo_part2.py
```
*See `docs/E2E_DEMO.md` for the full walkthrough of this process.*
