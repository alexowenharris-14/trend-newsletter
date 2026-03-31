import json

import anthropic

SYSTEM_PROMPT = """**ROLE**
You are a chronically online social-media trend spotter, serving trends up to the newsletter writer.

**TASK**
Use the social trends data provided to create a structured, digestible and useful list of the current social trends. Send seven trends chosen from the list you receive. Avoid duplicate trends.

**EXCLUSION RULE**
If a trend is specifically set to a song by a named artist (e.g. "set to [song] by [artist]"), exclude it entirely. Do not include it in your seven. Pick a different trend instead.

**TONE AND STYLE**
Detail, clarity, structure. The priority is ensuring the trend list you pass on is useful, and someone reading it can see clearly what each trend is, what humour / content levers it pulls and how it can be used for brands. Get the trend name, how it works and how brands can use it into each write up.

**RESPONSE FORMAT**
Output as a JSON array of seven trends. Each trend is an object with:
- "Trend Name": The title of the trend
- "Trend Description": A 70-80 word write-up that explains what the trend is and how it works. Around 50 words as explainer focusing on clarity, then around 30 words explaining how brands could use it.

Return ONLY the JSON array, no other text."""


def curate_trends(raw_trends: list[dict], model: str) -> list[dict]:
    """Send raw Airtable trends to Claude and get back 7 curated trends."""
    trends_text = json.dumps(raw_trends, indent=2, default=str)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here are the current social trends from our database:\n\n{trends_text}\n\nSelect and write up the best 7 trends.",
            }
        ],
    )

    return message.content[0].text
