import anthropic


TASK_PROMPT = """**TASK**
Turn the most current social trends input into a daily newsletter that will help the brand's social team jump on trends in a brand-relevant way.

Take the trends given to you as input. Turn these into a highly engaging newsletter structured as outlined below, in keeping with the brand tone of voice and creative approach defined in your knowledge base.

Explain the trends: what they are, how they work.

Add idea thought-starters after each trend explanation that could make it work for the brand (but not at the cost of clarity in the trend explanation). Keep ideas as short creative nudges, not full briefs. Follow the creative guidelines and checklist in your knowledge base to shape the ideas.

Make text edits and add context where relevant but still strictly adhere to the output format.

**Newsletter structure**

**Intro** Snappy intro that synthesises the trends through the brand lens to create a fun starting point to the newsletter. It should feel informative and not too try-hard funny. Strictly 25 words max.

**Hero Trend Name** Choose the one that feels like it has the most potency / cultural cache / energy.

**Hero Trend Description** A 70-80 word write-up that explains what the trend is and how it works. Around 50 words as explainer focusing on clarity, then around 30 words as a thought-starter idea for brand content.

**Trend Grid** An array of six trends, each represented as an object with the following two fields:
- name: the trend name (with emojis)
- description: a 50 word description of what it is and how to use it"""

OUTPUT_FORMAT_PROMPT = """**Output Formatting (STRICT)**
Return a JSON object only. Do not include markdown code blocks (no ```json), preamble, or conversational filler. Use this exact structure:

{
"Intro": "string",
"Hero Trend Name": "string",
"Hero Trend Description": "string",
"Trend Grid": [
{
"name": "string",
"description": "string"
}
]
}

Note: The "Trend Grid" must be a nested array of objects. Ensure all JSON syntax is valid and parsable."""


def write_newsletter(curated_trends: str, brand_config: str, model: str) -> str:
    """Send curated trends + brand voice to Claude and get back newsletter JSON."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system="You are a trend-obsessed, chronically online newsletter writer.",
        messages=[
            {"role": "user", "content": TASK_PROMPT},
            {"role": "user", "content": curated_trends},
            {
                "role": "assistant",
                "content": f"**This is my knowledge base**\n\n{brand_config}",
            },
            {"role": "user", "content": OUTPUT_FORMAT_PROMPT},
        ],
    )

    return message.content[0].text
