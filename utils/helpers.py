import json
import re

def load_test_data():
    with open('data/search_data.json', 'r') as f:
        return json.load(f)

def extract_price(text: str) -> float:
    try:
        text = text.split("to")[0]
        match = re.search(r"\d+(\.\d+)?", text)
        return float(match.group()) if match else float("inf")
    except Exception:
        return float("inf")