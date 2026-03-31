import json
import re


def extract_json(text: str) -> dict:
    """Extract a JSON object from LLM response text with fallback strategies."""
    text = text.strip()

    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown code fences
    fenced = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: find the outermost { ... } or [ ... ]
    for open_char, close_char in [("{", "}"), ("[", "]")]:
        start = text.find(open_char)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_char:
                depth += 1
            elif text[i] == close_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Could not extract valid JSON from LLM response:\n{text[:500]}")


def validate_newsletter_json(data: dict) -> dict:
    """Validate that newsletter JSON has the expected structure."""
    required_keys = ["Intro", "Hero Trend Name", "Hero Trend Description", "Trend Grid"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"Newsletter JSON missing required keys: {missing}")

    grid = data["Trend Grid"]
    if not isinstance(grid, list) or len(grid) == 0:
        raise ValueError("Trend Grid must be a non-empty array")

    for i, trend in enumerate(grid):
        if "name" not in trend or "description" not in trend:
            raise ValueError(f"Trend Grid item {i} missing 'name' or 'description'")

    return data
