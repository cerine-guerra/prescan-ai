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

## 🚀 How to Run the Project (For Team Members)

### 1️⃣ Create a Codespace

1. Go to the GitHub repository
2. Click the **Code** button (green)
3. Select **Codespaces** tab
4. Click **Create codespace on main**

> ⏱️ This takes 2-3 minutes to build the environment

---

### 2️⃣ Check Your Path

Once the Codespace opens, make sure you're in the correct directory:


# Check where you are
pwd

# You should be in: /workspaces/prescan-backend

# List files to verify
ls -la


3️⃣ Install Dependencies
bash
# Install all required Python packages
pip install -r requirements.txt

4️⃣ Download the AI Model ⚠️ IMPORTANT
The AI model is too large for GitHub, so you need to download it separately.

Download the model from Google Drive:

download the AI model from this link : 
https://colab.research.google.com/drive/1JP45Vq4RQf9ddk5b1JOgiIZXm2_kAPIl?usp=drive_link

Place the model in the correct folder:

bash
# Create the model directory if it doesn't exist
mkdir -p model

# Move the downloaded model file into the model folder
# The file is named : prescan_model.joblib
Verify the model is in place:

bash
ls -la model/
# You should see your model file(s)
📁 Expected model location: /workspaces/prescan-backend/model/prescan_model.joblib

5️⃣ Run the Server
bash
# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
You'll see:

text
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000

6️⃣ Make the Port Public
Important: The port needs to be public so the frontend can connect.

In the Codespace terminal, look for the Ports tab (next to Terminal)

Find port 8000 in the list

Right-click on it → Select "Port Visibility" → "Public"

You should see the visibility change from 🔒 Private to 🌐 Public
7️⃣ Access the Application
Once the port is public, open your browser and go to:

text
https://scaling-adventure-pjr47779j6p3gjq-8000.app.github.dev
Note: This is the shared API URL. When you run the server locally, your Codespace will have its own unique URL. Check the Ports tab for your specific URL.

To find your unique URL:

Go to the Ports tab

Hover over the "Address" column for port 8000

Click the 🌐 icon to open in browser

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
