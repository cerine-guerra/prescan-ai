from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
from parser import extract_text
from model_server import load_model, predict

app = FastAPI(title="Prescan AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    result = predict(combined)
    result["filename"] = file.filename
    result["sandbox_log"] = sandbox_log
    return result

class URLRequest(BaseModel):
    url: str

@app.post("/api/analyze-url")
async def analyze_url(body: URLRequest):
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(body.url, follow_redirects=True)
        text = r.text[:5000]
        final_url = str(r.url)
    except Exception as e:
        raise HTTPException(400, f"Could not fetch URL: {e}")
    result = predict(text)
    result["url"] = body.url
    result["final_url"] = final_url
    result["redirected"] = final_url != body.url
    return result

class ContactMsg(BaseModel):
    email: str
    message: str

@app.post("/api/contact")
async def contact(body: ContactMsg):
    print(f"[contact] {body.email}: {body.message}")
    return {"status": "received"}
