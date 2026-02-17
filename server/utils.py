import re
import json


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {"error": "Invalid JSON from AI"}
    return {"error": "No JSON found"}
