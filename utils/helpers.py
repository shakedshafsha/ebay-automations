import json
import re
from pathlib import Path

def load_test_data():
    path = Path(__file__).parent.parent / 'data' / 'search_data.json'
    with open(path, 'r') as f:
        return json.load(f)

def extract_price(text: str) -> float:
    try:
        text = text.split("to")[0]
        match = re.search(r"\d+(\.\d+)?", text)
        return float(match.group()) if match else float("inf")
    except Exception:
        return float("inf")