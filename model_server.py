import joblib
import numpy as np
import os
import math

# ── MODEL PATHS ──────────────────────────────────────────────
MALWARE_MODEL_PATH = os.getenv("MALWARE_MODEL_PATH", "./model/prescan_model.joblib")
URL_MODEL_PATH = os.getenv("URL_MODEL_PATH", "./model/url_model.pkl")

malware_model = None
url_model = None

# ── LOAD BOTH MODELS AT STARTUP ───────────────────────────────
def load_model():
    global malware_model, url_model

    # Load malware model (.joblib)
    if os.path.exists(MALWARE_MODEL_PATH):
        malware_model = joblib.load(MALWARE_MODEL_PATH)
        print(f"[model] ✓ Malware model loaded from {MALWARE_MODEL_PATH}")
    else:
        print(f"[model] ✗ Malware model not found at {MALWARE_MODEL_PATH} — using rules fallback")

    # Load URL model (.pkl)
    if os.path.exists(URL_MODEL_PATH):
        url_model = joblib.load(URL_MODEL_PATH)
        print(f"[model] ✓ URL model loaded from {URL_MODEL_PATH}")
    else:
        print(f"[model] ✗ URL model not found at {URL_MODEL_PATH} — using rules fallback")

    return malware_model is not None or url_model is not None


# ── SUSPICIOUS KEYWORDS LIST ──────────────────────────────────
SUSPICIOUS_KEYWORDS = [
    "eval(", "exec(", "subprocess", "powershell", "cmd.exe",
    "/bin/sh", "wget ", "curl -", "bitcoin", "ransom",
    "keylogger", "backdoor", "chmod 777", "rm -rf", "taskkill",
    "disable firewall", "base64", "reverse shell", "exploit",
    "payload", "dropper", "shellcode", "meterpreter", "mimikatz",
    "password", "/etc/passwd", "shadow", "encrypt", "decrypt",
    "socket", "connect(", "bind(", "listen(", "CreateRemoteThread",
    "VirtualAlloc", "WriteProcessMemory", "registry", "regedit"
]

SUSPICIOUS_URL_PATTERNS = [
    "login", "verify", "secure", "account", "update", "confirm",
    "banking", "paypal", "password", "credential", "signin",
    "free", "click", "prize", "winner", "lucky", "offer",
    "bit.ly", "tinyurl", "goo.gl", "t.co",
    ".exe", ".bat", ".ps1", ".vbs", ".zip", ".rar",
    "phish", "malware", "hack", "crack", "keygen",
    "192.168", "10.0.", "localhost", "127.0.0"
]


# ── FEATURE EXTRACTOR FOR FILES ───────────────────────────────
def extract_file_features(file_bytes: bytes) -> np.ndarray:
    features = []
    data = file_bytes

    # Byte histogram (256 features)
    histogram = np.zeros(256, dtype=np.float32)
    if len(data) > 0:
        for byte in data:
            histogram[byte] += 1
        histogram = histogram / len(data)
    features.extend(histogram.tolist())

    # Byte entropy per block (256 features)
    block_size = max(len(data) // 256, 1)
    block_entropies = []
    for i in range(256):
        start = i * block_size
        block = data[start:start + block_size]
        if not block:
            block_entropies.append(0.0)
            continue
        freq = {}
        for b in block:
            freq[b] = freq.get(b, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / len(block)
            if p > 0:
                entropy -= p * math.log2(p)
        block_entropies.append(entropy / 8.0)
    features.extend(block_entropies)

    # Text-based features (6 features)
    try:
        text = data.decode("utf-8", errors="ignore")
    except:
        text = ""
    printable = sum(1 for c in text if c.isprintable())
    features.append(min(printable / 100000.0, 1.0))
    words = text.split()
    avg_len = np.mean([len(w) for w in words]) if words else 0
    features.append(min(float(avg_len) / 100.0, 1.0))
    if len(text) > 0:
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        ent = -sum((v/len(text)) * math.log2(v/len(text)) for v in freq.values() if v > 0)
        features.append(ent / 8.0)
    else:
        features.append(0.0)
    features.append(min(text.lower().count("http") / 100.0, 1.0))
    features.append(min((text.count("/") + text.count("\\")) / 1000.0, 1.0))
    features.append(min((text.lower().count("hkey") + text.lower().count("registry")) / 100.0, 1.0))

    # General features (10 features)
    features.append(min(len(data) / 10000000.0, 1.0))
    features.append(0.0)
    features.append(0.0)
    features.append(min(text.lower().count("export") / 100.0, 1.0))
    features.append(min(text.lower().count("import") / 100.0, 1.0))
    features.append(0.0)
    features.append(1.0 if len(data) > 1000 else 0.0)
    features.append(0.0)
    features.append(min((text.lower().count("ssl") + text.lower().count("tls")) / 10.0, 1.0))
    features.append(min(sum(1 for c in text if not c.isalnum() and not c.isspace()) / 10000.0, 1.0))

    # Header/magic bytes (5 features)
    features.append(1.0 if data[:2] == b'MZ' else 0.0)
    features.append(1.0 if data[:4] == b'%PDF' else 0.0)
    features.append(1.0 if data[:2] == b'PK' else 0.0)
    features.append(1.0 if data[:4] == b'\x7fELF' else 0.0)
    features.append(1.0 if b'\x00' in data[:512] else 0.0)

    # Section/chunk features (5 features)
    chunk_size = max(len(data) // 5, 1)
    chunk_entropies = []
    for i in range(5):
        chunk = data[i*chunk_size:(i+1)*chunk_size]
        if not chunk:
            chunk_entropies.append(0.0)
            continue
        freq = {}
        for b in chunk:
            freq[b] = freq.get(b, 0) + 1
        ent = -sum((v/len(chunk)) * math.log2(v/len(chunk)) for v in freq.values() if v > 0)
        chunk_entropies.append(ent / 8.0)
    features.append(float(len(chunk_entropies)) / 20.0)
    features.append(float(np.mean(chunk_entropies)))
    features.append(float(np.max(chunk_entropies)))
    features.append(float(len(data) // 5) / 1000000.0)
    features.append(float(len(data)) / 1000000.0)

    # Import/export (3 features)
    features.append(min(text.lower().count("import") / 100.0, 1.0))
    features.append(min(len(text.split("(")) / 1000.0, 1.0))
    features.append(min(text.lower().count("export") / 100.0, 1.0))

    # Pad/trim to 541
    arr = np.array(features, dtype=np.float32)
    if len(arr) < 541:
        arr = np.pad(arr, (0, 541 - len(arr)))
    else:
        arr = arr[:541]
    return arr


# ── FEATURE EXTRACTOR FOR URLs ────────────────────────────────
def extract_url_features(url: str, page_text: str = "") -> np.ndarray:
    features = []
    url_lower = url.lower()
    combined = (url_lower + " " + page_text.lower())[:10000]

    # URL structural features (10 features)
    features.append(min(len(url) / 500.0, 1.0))                          # URL length
    features.append(url.count(".") / 10.0)                                # dot count
    features.append(url.count("-") / 10.0)                                # dash count
    features.append(url.count("_") / 10.0)                                # underscore count
    features.append(url.count("/") / 10.0)                                # slash count
    features.append(url.count("?") / 5.0)                                 # query params
    features.append(url.count("=") / 10.0)                                # param values
    features.append(url.count("@") / 2.0)                                 # @ sign (phishing)
    features.append(1.0 if "https" in url_lower else 0.0)                 # HTTPS
    features.append(1.0 if any(c.isdigit() for c in url_lower) else 0.0) # has numbers

    # Suspicious URL pattern features (16 features)
    for pattern in SUSPICIOUS_URL_PATTERNS:
        features.append(1.0 if pattern in combined else 0.0)

    # Domain features (6 features)
    try:
        domain = url.split("/")[2] if "//" in url else url.split("/")[0]
    except:
        domain = url
    features.append(min(len(domain) / 100.0, 1.0))                       # domain length
    features.append(domain.count(".") / 5.0)                              # subdomain depth
    features.append(1.0 if any(c.isdigit() for c in domain) else 0.0)    # IP-like domain
    features.append(1.0 if len(domain) > 30 else 0.0)                    # very long domain
    features.append(1.0 if domain.count("-") > 2 else 0.0)               # many dashes
    features.append(1.0 if "xn--" in domain else 0.0)                    # punycode (IDN homograph)

    # Page content features (8 features)
    if page_text:
        features.append(min(len(page_text) / 100000.0, 1.0))
        features.append(min(page_text.lower().count("password") / 10.0, 1.0))
        features.append(min(page_text.lower().count("login") / 10.0, 1.0))
        features.append(min(page_text.lower().count("verify") / 10.0, 1.0))
        features.append(min(page_text.lower().count("credit") / 10.0, 1.0))
        features.append(min(page_text.lower().count("bank") / 10.0, 1.0))
        features.append(1.0 if "<form" in page_text.lower() else 0.0)
        features.append(1.0 if "iframe" in page_text.lower() else 0.0)
    else:
        features.extend([0.0] * 8)

    # Pad/trim to 100 features
    arr = np.array(features, dtype=np.float32)
    if len(arr) < 100:
        arr = np.pad(arr, (0, 100 - len(arr)))
    else:
        arr = arr[:100]
    return arr


# ── PREDICT FOR FILES ─────────────────────────────────────────
def predict(sandbox_log: str, raw_bytes: bytes = None) -> dict:
    if malware_model is None:
        from rules_fallback import analyze_with_rules
        return analyze_with_rules(sandbox_log)

    try:
        if raw_bytes is not None:
            features = extract_file_features(raw_bytes)
        else:
            features = extract_file_features(sandbox_log.encode("utf-8"))

        proba = malware_model.predict_proba(features.reshape(1, -1))[0]
        malware_prob = float(proba[1])

        if malware_prob >= 0.75:
            verdict = "MALICIOUS"
        elif malware_prob >= 0.40:
            verdict = "SUSPICIOUS"
        else:
            verdict = "CLEAN"

        text_lower = sandbox_log.lower()
        flags = [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower]

        return {
            "verdict": verdict,
            "risk_score": round(malware_prob * 100),
            "confidence": round(malware_prob * 100 if verdict == "MALICIOUS" else (1 - malware_prob) * 100),
            "flags": flags,
            "source": "random_forest_malware"
        }

    except Exception as e:
        print(f"[malware_model] Error: {e} — falling back to rules")
        from rules_fallback import analyze_with_rules
        return analyze_with_rules(sandbox_log)


# ── PREDICT FOR URLs ──────────────────────────────────────────
def predict_url(url: str, page_text: str = "") -> dict:
    if url_model is None:
        from rules_fallback import analyze_with_rules
        return analyze_with_rules(url + " " + page_text)

    try:
        features = extract_url_features(url, page_text)
        proba = url_model.predict_proba(features.reshape(1, -1))[0]
        threat_prob = float(proba[1])

        if threat_prob >= 0.75:
            verdict = "MALICIOUS"
        elif threat_prob >= 0.40:
            verdict = "SUSPICIOUS"
        else:
            verdict = "CLEAN"

        combined = (url + " " + page_text).lower()
        flags = [p for p in SUSPICIOUS_URL_PATTERNS if p in combined]

        return {
            "verdict": verdict,
            "risk_score": round(threat_prob * 100),
            "confidence": round(threat_prob * 100 if verdict == "MALICIOUS" else (1 - threat_prob) * 100),
            "flags": flags,
            "source": "random_forest_url"
        }

    except Exception as e:
        print(f"[url_model] Error: {e} — falling back to rules")
        from rules_fallback import analyze_with_rules
        return analyze_with_rules(url)