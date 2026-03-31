import os
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_newsletter(newsletter_data: dict, output_dir: str) -> str:
    """Render newsletter data into an HTML file and return the file path."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("newsletter.html")

    html = template.render(
        intro=newsletter_data["Intro"],
        hero_trend_name=newsletter_data["Hero Trend Name"],
        hero_trend_description=newsletter_data["Hero Trend Description"],
        trend_grid=newsletter_data["Trend Grid"],
    )

    os.makedirs(output_dir, exist_ok=True)
    filename = f"newsletter_{date.today().isoformat()}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath
