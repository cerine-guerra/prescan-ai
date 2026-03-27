import io

def extract_text(content: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            return f"PDF parse error: {e}"
    elif ext in ("txt", "md", "log", "csv"):
        return content.decode("utf-8", errors="ignore")
    elif ext == "docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"DOCX parse error: {e}"
    return f"Unsupported extension: .{ext}"