"""Add metadata rows for curated company-profile markdown documents."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PROJECT_ROOT / "data" / "documents_metadata.csv"

METADATA_COLUMNS = [
    "original_filename",
    "new_filename",
    "title",
    "year",
    "entity",
    "category",
    "destination_folder",
    "source_type",
    "notes",
]

PROFILE_ROWS = [
    {
        "original_filename": "https://www.pif.gov.sa/en/our-investments/our-portfolio/humain/",
        "new_filename": "2025_pif_humain_company_profile.md",
        "title": "HUMAIN Company Profile",
        "year": "2025",
        "entity": "humain",
        "category": "company_profiles",
        "destination_folder": "data/company_profiles",
        "source_type": "web_profile",
        "notes": "Curated markdown profile from official PIF portfolio page.",
    },
    {
        "original_filename": "https://www.pif.gov.sa/en/our-investments/our-portfolio/saudi-company-for-artificial-intelligence/",
        "new_filename": "2025_pif_scai_company_profile.md",
        "title": "Saudi Company for Artificial Intelligence Company Profile",
        "year": "2025",
        "entity": "scai",
        "category": "company_profiles",
        "destination_folder": "data/company_profiles",
        "source_type": "web_profile",
        "notes": "Curated markdown profile from official PIF portfolio page.",
    },
    {
        "original_filename": "https://www.vision2030.gov.sa/en/explore/projects/alat",
        "new_filename": "2024_vision2030_alat_company_profile.md",
        "title": "Alat Company Profile",
        "year": "2024",
        "entity": "alat",
        "category": "company_profiles",
        "destination_folder": "data/company_profiles",
        "source_type": "web_profile",
        "notes": "Curated markdown profile from official Vision 2030 project page.",
    },
]


def read_rows() -> list[dict[str, str]]:
    """Read existing metadata rows."""
    if not METADATA_PATH.exists():
        return []

    with METADATA_PATH.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [{column: row.get(column, "") for column in METADATA_COLUMNS} for row in reader]


def write_rows(rows: list[dict[str, str]]) -> None:
    """Write metadata rows."""
    with METADATA_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Add missing company profile metadata rows."""
    rows = read_rows()
    existing = {row["new_filename"] for row in rows}

    added = 0
    for row in PROFILE_ROWS:
        if row["new_filename"] not in existing:
            rows.append(row)
            added += 1

    write_rows(rows)
    print(f"Added {added} company profile metadata row(s).")


if __name__ == "__main__":
    main()
