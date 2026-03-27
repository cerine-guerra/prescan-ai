THREAT_KEYWORDS = [
    "eval(", "exec(", "subprocess", "os.system",
    "rm -rf", "wget ", "curl ", "chmod 777",
    "password", "credit card", "bitcoin",
    "encrypt", "ransom", "keylog", "backdoor",
    "/etc/passwd", "disable firewall", "taskkill"
]

def analyze_with_rules(text: str) -> dict:
    text_lower = text.lower()
    found = [kw for kw in THREAT_KEYWORDS if kw in text_lower]
    score = min(len(found) * 18, 100)
    if score >= 55:
        verdict = "MALICIOUS"
    elif score >= 20:
        verdict = "SUSPICIOUS"
    else:
        verdict = "CLEAN"
    return {
        "verdict": verdict,
        "risk_score": score,
        "flags": found,
        "confidence": 72.0,
        "source": "rules_fallback"
    }