import torch, os

model = None

def load_model():
    global model
    path = os.getenv("MODEL_PATH", "./model/prescan_model.pt")
    if os.path.exists(path):
        model = torch.load(path, map_location="cpu")
        model.eval()
        print(f"[model] Loaded from {path}")
        return True
    print("[model] Not found — using rules fallback")
    return False

def predict(text: str) -> dict:
    if model is None:
        from rules_fallback import analyze_with_rules
        return analyze_with_rules(text)
    # Your teammate fills this part in once model is ready
    from rules_fallback import analyze_with_rules
    return analyze_with_rules(text)