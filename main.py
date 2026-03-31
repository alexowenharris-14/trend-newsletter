import argparse
import io
import json
import sys
from pathlib import Path

# Fix Windows console emoji encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import yaml
from dotenv import load_dotenv

from src.airtable_client import fetch_trends
from src.trend_curator import curate_trends
from src.newsletter_writer import write_newsletter
from src.json_parser import extract_json, validate_newsletter_json
from src.html_renderer import render_newsletter


def load_config(config_path: str = "config/settings.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_brand(brand_path: str = "config/brand.md") -> str:
    with open(brand_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Generate a trend newsletter")
    parser.add_argument("--config", default="config/settings.yaml", help="Path to settings YAML")
    parser.add_argument("--brand", default="config/brand.md", help="Path to brand voice config")
    parser.add_argument("--output", default=None, help="Output directory (overrides settings.yaml)")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and curate only, print JSON without rendering HTML")
    args = parser.parse_args()

    load_dotenv()

    config = load_config(args.config)
    brand_config = load_brand(args.brand)
    output_dir = args.output or config["output"]["directory"]

    # Step 1: Fetch trends from Airtable
    print("[1/5] Fetching trends from Airtable...")
    airtable = config["airtable"]
    raw_trends = fetch_trends(
        base_id=airtable["base_id"],
        table_name=airtable["table_name"],
        max_records=airtable["max_records"],
    )
    print(f"      Fetched {len(raw_trends)} trends.")

    # Step 2: Curate trends via LLM
    print("[2/5] Curating trends with Claude...")
    curator_model = config["anthropic"]["curator_model"]
    curated_text = curate_trends(raw_trends, model=curator_model)
    curated_trends = extract_json(curated_text)
    print(f"      Curated {len(curated_trends)} trends.")

    if args.dry_run:
        print("\n--- DRY RUN: Curated trends ---")
        print(json.dumps(curated_trends, indent=2))
        return

    # Step 3: Write newsletter via LLM
    print("[3/5] Writing newsletter with Claude...")
    writer_model = config["anthropic"]["writer_model"]
    curated_json_str = json.dumps(curated_trends, indent=2)
    newsletter_text = write_newsletter(curated_json_str, brand_config, model=writer_model)

    # Step 4: Parse and validate
    print("[4/5] Parsing newsletter JSON...")
    newsletter_data = extract_json(newsletter_text)
    newsletter_data = validate_newsletter_json(newsletter_data)
    print(f"      Hero trend: {newsletter_data['Hero Trend Name']}")
    print(f"      Grid trends: {len(newsletter_data['Trend Grid'])}")

    # Step 5: Render HTML
    print("[5/5] Rendering HTML...")
    filepath = render_newsletter(newsletter_data, output_dir)
    print(f"      Newsletter saved to: {filepath}")


if __name__ == "__main__":
    main()
