from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()
from parser import extract_text
from model_server import load_model, predict, predict_url

app = FastAPI(title="Prescan AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.on_event("startup")
async def startup():
    load_model()

@app.get("/health")
def health():
    return {"status": "ok"}

ALLOWED_EXT = {"pdf", "txt", "docx", "csv", "md", "log"}
MAX_MB = int(os.getenv("MAX_FILE_MB", 10))

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"File type .{ext} not allowed")
    content = await file.read()
    if len(content) > MAX_MB * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {MAX_MB}MB limit")

    from sandbox import run_sandbox
    sandbox_log = run_sandbox(content, file.filename)
    text = extract_text(content, file.filename)
    combined = sandbox_log + "\n" + text[:3000]
    result = predict(combined, raw_bytes=content)
    result["filename"] = file.filename
    result["sandbox_log"] = sandbox_log
    return result

class URLRequest(BaseModel):
    url: str

class ContactMsg(BaseModel):
    email: str
    message: str

@app.post("/api/analyze-url")
async def analyze_url(body: URLRequest):
    import httpx

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    page_text = ""
    final_url = body.url
    redirected = False
    fetch_status = "success"

    try:
        async with httpx.AsyncClient(
            timeout=8,
            headers=headers,
            follow_redirects=True
        ) as client:
            r = await client.get(body.url)
            page_text = r.text[:5000]
            final_url = str(r.url)
            redirected = final_url != body.url

    except httpx.TimeoutException:
        fetch_status = "timeout"

    except httpx.ConnectError:
        fetch_status = "unreachable"

    except Exception:
        fetch_status = "error"

    result = predict_url(body.url, page_text)
    result["url"] = body.url
    result["final_url"] = final_url
    result["redirected"] = redirected

    if fetch_status == "unreachable":
        result["note"] = "Domain unreachable — URL structure analyzed only"
        result["risk_score"] = min(result["risk_score"] + 20, 100)
        if result["verdict"] == "CLEAN":
            result["verdict"] = "SUSPICIOUS"

    elif fetch_status == "timeout":
        result["note"] = "Request timed out — URL structure analyzed only"
        result["risk_score"] = min(result["risk_score"] + 10, 100)

    return result

@app.post("/api/contact")
async def contact(body: ContactMsg):
    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    mail_email = os.getenv("MAIL_EMAIL")
    mail_password = os.getenv("MAIL_PASSWORD")

    # Build the email
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Prescan AI — New Message from {body.email}"
    message["From"] = mail_email
    message["To"] = mail_email

    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2563eb;">New Contact Message — Prescan AI</h2>
        <hr style="border-color: #39ff6e;">
        <p><strong>From:</strong> {body.email}</p>
        <p><strong>Message:</strong></p>
        <div style="background:#f5f5f5; padding:15px; border-radius:8px;">
            {body.message}
        </div>
        <hr>
        <p style="color:#999; font-size:12px;">Sent via Prescan AI contact form</p>
    </body></html>
    """

    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=465,
            username=mail_email,
            password=mail_password,
            use_tls=True,
        )
        print(f"[contact] Email sent from {body.email}")
        return {"status": "sent"}

    except Exception as e:
        print(f"[contact] Email failed: {e}")
        raise HTTPException(500, "Failed to send email. Please try again.")