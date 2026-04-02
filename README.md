#🔍 Prescan AI — Threat Detection Platform

AI-powered malware and phishing detection. Upload a file or paste a URL to instantly scan for threats, risks, and dangers.

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


📋 Table of Contents

Project Overview
Tech Stack
Project Structure
Getting Started (New Collaborator)
Running the Project
API Endpoints
AI Models
Environment Variables
Important Notes


Project Overview
Prescan AI is a cybersecurity web application that uses machine learning to detect malware in files and phishing threats in URLs. It consists of:

A Vue.js frontend with a dark cybersecurity-themed UI
A FastAPI Python backend with REST API endpoints
A Docker sandbox that isolates and analyzes files safely
Two Random Forest AI models — one for file malware detection, one for URL threat detection
A rules-based fallback engine that activates if models are unavailable


Tech Stack
LayerTechnologyFrontendVue.js 3, Tailwind CSS, jsPDFBackendPython, FastAPI, UvicornAI Modelsscikit-learn 1.6.1, Random ForestSandboxDocker (isolated container)File ParsingPyPDF2, python-docx, pandasURL Scanninghttpx (async HTTP client)Emailaiosmtplib (Gmail SMTP)HostingGitHub Codespaces

Project Structure
prescan-backend/
├── frontend/
│   └── index.html              ← Vue.js single-page frontend
├── main.py                     ← FastAPI app — all API routes
├── model_server.py             ← AI model loader and predict functions
├── parser.py                   ← File text extractor (PDF, DOCX, CSV, TXT)
├── rules_fallback.py           ← Keyword-based fallback detection engine
├── sandbox.py                  ← Docker sandbox wrapper
├── sandbox-image/
│   ├── Dockerfile              ← Sandbox container definition
│   └── analyze.py              ← Behavior monitor (runs inside container)
├── model/
│   ├── prescan_model.joblib    ← Malware detection model (not on GitHub)
│   └── url_model.pkl           ← URL threat detection model (not on GitHub)
├── .env                        ← Secret credentials (not on GitHub)
├── .gitignore
└── README.md

Getting Started (New Collaborator)
Follow these steps in order after accepting the GitHub collaboration invite.
Step 1 — Open the project in Codespaces

Go to the shared GitHub repository
Click the green Code button
Click the Codespaces tab
Click Create codespace on main

Wait for the Codespace to load fully before continuing.
Step 2 — Install all dependencies
Open the terminal inside Codespaces and run:
bashcd /workspaces/prescan-backend

pip install fastapi uvicorn python-multipart python-dotenv \
    httpx torch PyPDF2 python-docx scikit-learn==1.6.1 \
    joblib aiosmtplib aiofiles docker

⚠️ Important: You must use scikit-learn==1.6.1 exactly. Other versions will cause a version mismatch error when loading the models.

Step 3 — Create the .env file
you can also get ut directly from the google drive folder

Step 4 — Upload the AI model files
The model files are too large for GitHub. Get them from the project lead via Google Drive, then upload them:

In VS Code file explorer, right-click the model/ folder
Click Upload
Upload prescan_model.joblib

Verify they uploaded correctly:
bashls -lh /workspaces/prescan-backend/model/
Both files should be several MB in size. If they show KB, the upload was incomplete — try again.
Step 5 — Build the Docker sandbox image
bashdocker build -t prescan-sandbox /workspaces/prescan-backend/sandbox-image/
This takes about 2 minutes. You should see Successfully tagged prescan-sandbox:latest at the end.
Step 6 — Update the frontend API URL
Your Codespace has a different URL from the project lead's. Find your URL:
bashecho "https://${CODESPACE_NAME}-8000.app.github.dev"
Open frontend/index.html and update this line near the top of the JavaScript section:
javascriptconst API_BASE = 'https://YOUR-CODESPACE-URL-8000.app.github.dev';

Running the Project
Start the API server
bashcd /workspaces/prescan-backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Make port 8000 public
In VS Code, click the Ports tab at the bottom → right-click port 8000 → Port Visibility → Public
Verify the server is running
Open this URL in your browser:
https://YOUR-CODESPACE-URL-8000.app.github.dev/health
You should see:
json{"status": "ok"}
Open the frontend
Double-click frontend/index.html on your local PC to open it in the browser. The frontend connects to your Codespace API automatically.
Keep the server running in the background
If you want the server to keep running after closing the terminal:
bashnohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
Check if it is running:
bashcurl http://localhost:8000/health
View live logs:
bashtail -f server.log
Stop the server:
bashpkill -f uvicorn

API Endpoints
MethodEndpointDescriptionGET/healthCheck if server is runningPOST/api/analyzeScan an uploaded file for malwarePOST/api/analyze-urlScan a URL for phishing threatsPOST/api/contactSend a contact form email
File Analysis — POST /api/analyze
Request: multipart/form-data with a file field
Accepted formats: .pdf, .txt, .docx, .csv, .md, .log
Max file size: 10 MB (configurable in .env)
Response:
json{
  "verdict": "MALICIOUS",
  "risk_score": 95,
  "confidence": 95,
  "flags": ["eval(", "exec(", "ransom"],
  "source": "random_forest_malware",
  "filename": "test.txt",
  "sandbox_log": "FILE_SIZE: 38 bytes\nENTROPY: 4.05\n..."
}
URL Analysis — POST /api/analyze-url
Request:
json{ "url": "https://example.com" }
Response:
json{
  "verdict": "CLEAN",
  "risk_score": 12,
  "confidence": 88,
  "flags": [],
  "source": "random_forest_url",
  "url": "https://example.com",
  "final_url": "https://example.com",
  "redirected": false
}
Verdict meanings
VerdictRisk ScoreMeaningCLEAN0 – 39No threats detectedSUSPICIOUS40 – 74Potentially dangerous, review recommendedMALICIOUS75 – 100High confidence threat detected

AI Models
Malware Detection Model (prescan_model.joblib)

Algorithm: Random Forest (200 trees)
Trained on: EMBER 2018 dataset (150,000+ PE file samples)
Features: Byte histogram, entropy, string patterns, file structure
Accuracy: ~97%
Used for: File uploads

URL Threat Detection Model (url_model.pkl)

Algorithm: Random Forest
Features: URL structure, domain patterns, page content analysis
Used for: URL scanning

Fallback Engine (rules_fallback.py)
If either model file is not found, the system automatically falls back to a keyword-based rules engine. The source field in the response will show rules_fallback instead of random_forest_malware or random_forest_url.

Environment Variables
VariableDescriptionExampleMALWARE_MODEL_PATHPath to malware model file./model/prescan_model.joblibURL_MODEL_PATHPath to URL model file./model/url_model.pklMAX_FILE_MBMaximum upload file size in MB10MAIL_EMAILGmail address for contact formvectorshield2026@gmail.comMAIL_PASSWORDGmail App Password (16 characters)xxxx xxxx xxxx xxxx

Important Notes
Never commit these files to GitHub:

.env — contains email credentials
model/*.joblib and model/*.pkl — model files are too large and contain proprietary training

Codespace idle timeout: Set your idle timeout to 4 hours before a demo to prevent the Codespace from sleeping. Go to github.com/settings/codespaces and update the setting.
Port visibility: Every time you create a new Codespace, you must set port 8000 to Public in the Ports tab. It resets to Private by default.
sklearn version: Always use scikit-learn==1.6.1. The models were trained with this version and will throw warnings or errors with newer versions.
Docker sandbox: The sandbox runs files in a fully isolated container with no internet access and a 30-second timeout. It is safe to test with suspicious-looking files — they cannot escape the container.

Contact
Email: vectorshield2026@gmail.com
Team: Prescan AI — Built for the 2026 hackathon
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
