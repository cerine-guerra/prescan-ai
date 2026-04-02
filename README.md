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

📁 Project Structure
```
prescan-backend/
│
├── frontend/
│   └── index.html                # Vue.js single-page frontend
│
├── main.py                       # FastAPI app — API routes entrypoint
├── model_server.py               # AI model loading & prediction logic
├── parser.py                     # File text extraction (PDF, DOCX, CSV, TXT)
├── rules_fallback.py             # Keyword-based fallback detection engine
├── sandbox.py                    # Docker sandbox wrapper
│
├── sandbox-image/               # Sandbox environment
│   ├── Dockerfile                # Container definition
│   └── analyze.py                # Behavior analysis (runs inside container)
│
├── model/                       # AI models (not tracked in Git)
│   ├── prescan_model.joblib      # Malware detection model
│   └── url_model.pkl             # URL threat detection model
│
├── .env                          # Environment variables (not committed)
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

🚀 Getting Started (New Collaborator)

Follow these steps carefully after accepting the GitHub collaboration invite.

1. Open the Project in Codespaces
Navigate to the shared repository on GitHub
Click the green “Code” button
Go to the Codespaces tab
Click “Create codespace on main”

⏳ Wait until the Codespace is fully loaded before proceeding.

2. Install Dependencies

Open the terminal inside Codespaces and run:

cd /workspaces/prescan-backend

pip install fastapi uvicorn python-multipart python-dotenv \
    httpx torch PyPDF2 python-docx scikit-learn==1.6.1 \
    joblib aiosmtplib aiofiles docker

⚠️ Important:
Use scikit-learn==1.6.1 exactly. Other versions will cause model loading errors.

3. Create the .env File

You can:

Request the .env file from the project lead, or
Download it from the shared Google Drive folder
4. Upload AI Model Files

The model files are too large for GitHub. Download them from Google Drive, then:

Open the file explorer in VS Code
Right-click the model/ folder
Click Upload
Upload the following files:
prescan_model.joblib
url_model.pkl
Verify Upload
ls -lh /workspaces/prescan-backend/model/

✔ Files should be several MB in size
❌ If they appear in KB, the upload failed — try again

5. Build the Docker Sandbox
docker build -t prescan-sandbox /workspaces/prescan-backend/sandbox-image/

⏳ This takes about 2 minutes
✅ Success message:

Successfully tagged prescan-sandbox:latest
6. Update the Frontend API URL

Your Codespace has a unique URL. Generate it with:

echo "https://${CODESPACE_NAME}-8000.app.github.dev"

Then:

Open frontend/index.html
Locate the API base URL in the JavaScript section
Replace it with your Codespace URL:
const API_BASE = 'https://YOUR-CODESPACE-URL-8000.app.github.dev';
▶️ Running the Project
Start the API Server
cd /workspaces/prescan-backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Make Port Public
Go to the Ports tab in VS Code
Right-click port 8000
Select Port Visibility → Public
Verify the Server

Open in your browser:

https://YOUR-CODESPACE-URL-8000.app.github.dev/health

Expected response:

{"status": "ok"}
Open the Frontend
Open frontend/index.html on your local machine
It will automatically connect to your Codespace API
Keep Server Running in Background
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
Useful Commands

Check status:

curl http://localhost:8000/health

View logs:

tail -f server.log

Stop server:

pkill -f uvicorn
📡 API Endpoints
Method	Endpoint	Description
GET	/health	Check if server is running
POST	/api/analyze	Scan uploaded files
POST	/api/analyze-url	Scan URLs for threats
POST	/api/contact	Send contact form email
📁 File Analysis — /api/analyze

Request:
multipart/form-data with a file field

Supported formats:
.pdf, .txt, .docx, .csv, .md, .log

Max size: 10 MB (configurable in .env)

Response:

{
  "verdict": "MALICIOUS",
  "risk_score": 95,
  "confidence": 95,
  "flags": ["eval(", "exec(", "ransom"],
  "source": "random_forest_malware",
  "filename": "test.txt",
  "sandbox_log": "..."
}
🌐 URL Analysis — /api/analyze-url

Request:

{ "url": "https://example.com" }

Response:

{
  "verdict": "CLEAN",
  "risk_score": 12,
  "confidence": 88,
  "flags": [],
  "source": "random_forest_url",
  "url": "https://example.com",
  "final_url": "https://example.com",
  "redirected": false
}
⚖️ Verdict Meaning
Verdict	Risk Score	Meaning
CLEAN	0–39	No threats detected
SUSPICIOUS	40–74	Potential risk — review recommended
MALICIOUS	75–100	High confidence threat detected
🤖 AI Models
Malware Detection
File: prescan_model.joblib
Algorithm: Random Forest (200 trees)
Dataset: EMBER 2018 (150K+ samples)
Accuracy: ~97%
Features: Byte patterns, entropy, structure
URL Detection
File: url_model.pkl
Algorithm: Random Forest
Features: URL structure, domain patterns
Fallback System

If models are unavailable, a rule-based engine is used automatically.

🌍 Environment Variables
Variable	Description	Example
MALWARE_MODEL_PATH	Path to malware model	/model/prescan_model.joblib
URL_MODEL_PATH	Path to URL model	/model/url_model.pkl
MAX_FILE_MB	Max upload size	10
MAIL_EMAIL	Gmail address	vectorshield2026@gmail.com
MAIL_PASSWORD	Gmail App Password	xxxx xxxx xxxx xxxx
⚠️ Important Notes
❌ Never commit:
.env
model/*.joblib
model/*.pkl
⏱️ Codespace idle timeout:
Set to 4 hours before demos to prevent sleep.
🔓 Port visibility:
Must manually set port 8000 to Public each time.
📦 scikit-learn:
Always use version 1.6.1
🛡️ Docker sandbox:
Runs in isolation with:
No internet access
30-second timeout
Safe execution environment

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



📬 Contact
Email: vectorshield2026@gmail.com
Team: Prescan AI — Built for the 2026 IACE Competition

---
Built with ❤️ for Security Automation
