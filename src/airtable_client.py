import os
import requests


def fetch_trends(base_id: str, table_name: str, max_records: int = 10) -> list[dict]:
    """Fetch the latest trends from Airtable, sorted by Date descending."""
    api_key = os.environ["AIRTABLE_API_KEY"]

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    params = {
        "maxRecords": max_records,
        "sort[0][field]": "Date",
        "sort[0][direction]": "desc",
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    records = response.json().get("records", [])
    return [record["fields"] for record in records if "fields" in record]
