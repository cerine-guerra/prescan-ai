import sys, os, hashlib, math

filepath = sys.argv[1] if len(sys.argv) > 1 else "/sample/file"

if not os.path.exists(filepath):
    print("ERROR: file not found")
    sys.exit(1)

with open(filepath, "rb") as f:
    data = f.read()

null_byte = b'\x00'
newline = chr(10)

print(f"FILE_SIZE: {len(data)} bytes")
print(f"MD5: {hashlib.md5(data).hexdigest()}")
print(f"EXTENSION: {filepath.rsplit('.', 1)[-1].lower()}")
print(f"NULL_BYTES: {data.count(null_byte)}")

if len(data) > 0:
    freq = [data.count(bytes([i])) / len(data) for i in range(256)]
    entropy = -sum(p * math.log2(p) for p in freq if p > 0)
    print(f"ENTROPY: {entropy:.2f}")
else:
    print("ENTROPY: 0")

SUSPICIOUS = [
    "eval(", "exec(", "import os", "subprocess", "powershell",
    "/bin/sh", "cmd.exe", "wget", "curl -", "bitcoin",
    "ransom", "keylogger", "backdoor", "chmod 777",
    "rm -rf", "taskkill", "disable firewall", "base64",
    "reverse shell", "exploit", "payload", "dropper"
]

try:
    text = data.decode("utf-8", errors="ignore")
    found = [kw for kw in SUSPICIOUS if kw.lower() in text.lower()]
    keywords = ','.join(found) if found else 'none'
    preview = text[:300].replace(newline, ' ')
    print(f"SUSPICIOUS_KEYWORDS: {keywords}")
    print(f"TEXT_PREVIEW: {preview}")
except Exception as e:
    print(f"DECODE_ERROR: {e}")
