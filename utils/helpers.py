import json
import re

def load_test_data():
    with open('data/test_data.json', 'r') as f:
        return json.load(f)

def extract_price(text: str) -> float:
        try:
            clean = re.sub(r"[^\d.]", "", text.split("to")[0])
            return float(clean)
        except Exception:
            return float("inf")