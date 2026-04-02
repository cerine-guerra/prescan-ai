# 🛡️ Prescan AI Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.10+](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**Prescan AI** is a lightweight, scalable backend designed for automated security analysis of files and URLs. It utilizes an isolated Docker sandbox environment for safe code execution, text extraction, and a dynamic analysis engine supported by both Machine Learning (PyTorch) and a robust Rule-Based heuristic fallback.

## ✨ Features

- **Document Parsing**: Native text extraction for `.pdf`, `.docx`, `.txt`, `.csv`, `.md`, and `.log` formats.
- **URL & Phishing Analysis**: Safely fetches remote resources, traces redirects, and scans web page text for malicious signatures.
- **Docker Sandbox Execution**: Suspicious files are run within an isolated `prescan-sandbox` Docker container to extract execution logs without risking host machine integrity.
- **Machine Learning & Heuristics**: Automatically loads specialized `.pt` PyTorch models for AI-driven detection. Defaults to a high-speed keyword heuristic engine if models aren't available.
- **CORS-Ready & Robust**: Built atop FastAPI and Uvicorn, ready to handle cross-origin requests from any frontend tier.

## 📁 Project Structure

```text
prescan-backend/
├── main.py             # FastAPI entry point & API endpoints
├── model_server.py     # ML Model loader and prediction logic
├── parser.py           # Document text extraction utilities
├── rules_fallback.py   # Heuristic keyword-based analysis engine
├── sandbox.py          # Docker container orchestration logic
├── sandbox-image/      # Docker context for the analysis sandbox
│   ├── Dockerfile      # Sandbox image definition
│   └── analyze.py      # Script that runs inside the container
├── model/              # Directory for trained PyTorch models (.pt)
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker Engine** (required for sandbox execution)
- **PyTorch** (for the ML aspect)

### Installation

1. **Clone and Setup Environment**:

   ```bash
   cp .env.example .env
   # Adjust environment variables in .env as needed
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Build the Sandbox**:
   The sandbox isolates untrusted files during analysis.

   ```bash
   cd sandbox-image
   docker build -t prescan-sandbox .
   cd ..
   ```

4. **Launch the API**:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🔌 API Endpoints

### 1. File Analysis (`POST /api/analyze`)

Upload a file using `multipart/form-data`. The file will be passed through text extraction and isolated sandbox execution, before being scored for risk.

**Parameters**:

- `file`: The document to be analyzed (PDF, DOCX, CSV, TXT, etc.). Maximum size configurable via `.env` (`MAX_FILE_MB`).

**Response Example**:

```json
{
  "verdict": "SUSPICIOUS",
  "risk_score": 36,
  "flags": ["eval(", "subprocess"],
  "confidence": 72.0,
  "source": "rules_fallback",
  "filename": "suspicious.py",
  "sandbox_log": "..."
}
```

### 2. URL Analysis (`POST /api/analyze-url`)

Inspect a URL for malicious intent or phishing redirects.

**Request Body (`application/json`)**:

```json
{
  "url": "http://suspicious-site.test"
}
```

### 3. Service Health (`GET /health`)

Quick availability ping to ensure the API is running.

## 🧠 ML Model Integration

The project attempts to load a PyTorch model defined in `MODEL_PATH` upon startup.

- **Loading Logic**: If the model file is missing or invalid, the system gracefully reverts to **Rule-Based Analysis**.
- **Usage**:
  1. Save your PyTorch weights as `./model/prescan_model.pt`.
  2. Modify the `predict()` function in `model_server.py` to bridge your specific model architecture.

## 🛡️ Architecture & Security

This application handles untrusted and potentially malicious artifacts.

- **Sandboxing**: Docker containers are run with `network_disabled=True` and `mem_limit` to prevent resource exhaustion and lateral movement.
- **Parser Isolation**: Only text is extracted from documents on the host; the full file binary is analyzed only within the sandbox.
- **Production Note**: Do not expose this API directly to the internet without implementing rate-limiting and authentication via a proxy.

---
Built with ❤️ for Security Automation
