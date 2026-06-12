"""Download recommended official documents for the Saudi AI Career RAG dataset.

Run from the project root:
    python scripts/download_recommended_documents.py
"""

from __future__ import annotations

import csv
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
METADATA_PATH = DATA_DIR / "documents_metadata.csv"

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


@dataclass(frozen=True)
class RecommendedDocument:
    """One official document to add to the local RAG dataset."""

    url: str
    category: str
    filename: str
    title: str
    year: str
    entity: str
    notes: str


DOCUMENTS = [
    RecommendedDocument(
        url="https://www.vision2030.gov.sa/media/25042025ev1/En-Annual%20Report-Vision2030-2024.pdf",
        category="vision_reports",
        filename="2024_vision2030_annual_report.pdf",
        title="Vision 2030 Annual Report 2024",
        year="2024",
        entity="vision2030",
        notes="Official Vision 2030 annual report.",
    ),
    RecommendedDocument(
        url="https://www.vision2030.gov.sa/media/ecdjfopq/vision2030_annual_report_2025_en.pdf",
        category="vision_reports",
        filename="2025_vision2030_annual_report.pdf",
        title="Vision 2030 Annual Report 2025",
        year="2025",
        entity="vision2030",
        notes="Official Vision 2030 annual report.",
    ),
    RecommendedDocument(
        url="https://www.vision2030.gov.sa/media/pgid4z3t/2021-2025-human-capability-development-program-delivery-plan-en.pdf",
        category="human_capital",
        filename="2021_hcdp_delivery_plan_2021_2025.pdf",
        title="Human Capability Development Program Delivery Plan 2021-2025",
        year="2021",
        entity="hcdp",
        notes="Official Vision 2030 delivery plan focused on education, training, and workforce capabilities.",
    ),
    RecommendedDocument(
        url="https://www.hrsd.gov.sa/sites/default/files/2025-02/Digital%20Sector%20Skills%20Intro%20Report_EN.pdf",
        category="human_capital",
        filename="2025_hrsd_digital_sector_skills_intro_report.pdf",
        title="Digital Sector Skills Intro Report",
        year="2025",
        entity="hrsd",
        notes="Official HRSD sector skills report for digital occupations and skills.",
    ),
    RecommendedDocument(
        url="https://www.hrsd.gov.sa/sites/default/files/2025-02/Tourism%20and%20Hospitality%20Sector%20Skills%20Dictionary_EN.pdf",
        category="human_capital",
        filename="2025_hrsd_tourism_hospitality_sector_skills_dictionary.pdf",
        title="Tourism and Hospitality Sector Skills Dictionary",
        year="2025",
        entity="hrsd",
        notes="Official HRSD sector skills dictionary.",
    ),
    RecommendedDocument(
        url="https://www.hrsd.gov.sa/sites/default/files/2025-02/Professional%20and%20Consulting%20Services%20Sector%20Skills%20Dictionary_EN.pdf",
        category="human_capital",
        filename="2025_hrsd_professional_consulting_services_skills_dictionary.pdf",
        title="Professional and Consulting Services Sector Skills Dictionary",
        year="2025",
        entity="hrsd",
        notes="Official HRSD sector skills dictionary.",
    ),
    RecommendedDocument(
        url="https://www.stats.gov.sa/documents/20117/2435273/LMS%2BQ2_2025_EN.pdf/c596f7f3-bfce-007a-b0ed-83792da1654f",
        category="sector_programs",
        filename="2025_gastat_labor_market_statistics_q2.pdf",
        title="Labor Market Statistics Q2 2025",
        year="2025",
        entity="gastat",
        notes="Official GASTAT labor market bulletin.",
    ),
    RecommendedDocument(
        url="https://www.stats.gov.sa/documents/20117/2435273/LMS%2BQ3_2025%2BEN.pdf/6fba3faf-5cba-a828-51c9-dc74278856d0",
        category="sector_programs",
        filename="2025_gastat_labor_market_statistics_q3.pdf",
        title="Labor Market Statistics Q3 2025",
        year="2025",
        entity="gastat",
        notes="Official GASTAT labor market bulletin.",
    ),
    RecommendedDocument(
        url="https://sdaia.gov.sa/en/SDAIA/about/Documents/ai-principles.pdf",
        category="ai_governance",
        filename="2023_sdaia_ai_ethics_principles.pdf",
        title="AI Ethics Principles",
        year="2023",
        entity="sdaia",
        notes="Official SDAIA AI ethics principles and controls.",
    ),
    RecommendedDocument(
        url="https://nca.gov.sa/scywf_en.pdf",
        category="human_capital",
        filename="2020_nca_saudi_cybersecurity_workforce_framework.pdf",
        title="Saudi Cybersecurity Workforce Framework",
        year="2020",
        entity="nca",
        notes="Official NCA workforce framework covering cybersecurity roles, tasks, knowledge, skills, and abilities.",
    ),
]


def ensure_folder_structure() -> None:
    """Create all destination folders needed by this downloader."""
    for document in DOCUMENTS:
        (DATA_DIR / document.category).mkdir(parents=True, exist_ok=True)


def unique_destination_path(path: Path) -> Path:
    """Return a collision-safe path by appending _v2, _v3, and so on."""
    if not path.exists():
        return path

    version = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{version}{path.suffix}")
        if not candidate.exists():
            return candidate
        version += 1


def download_file(url: str, destination: Path) -> None:
    """Download a URL to a destination path."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Saudi-AI-Career-RAG/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        with destination.open("wb") as output_file:
            shutil.copyfileobj(response, output_file)


def read_existing_metadata() -> list[dict[str, str]]:
    """Read existing metadata rows if the CSV exists."""
    if not METADATA_PATH.exists():
        return []

    with METADATA_PATH.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            {column: row.get(column, "") for column in METADATA_COLUMNS}
            for row in reader
        ]


def write_metadata(rows: list[dict[str, str]]) -> None:
    """Write metadata rows with a stable schema."""
    with METADATA_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def metadata_row(document: RecommendedDocument, filename: str) -> dict[str, str]:
    """Build one metadata row for a downloaded document."""
    return {
        "original_filename": document.url,
        "new_filename": filename,
        "title": document.title,
        "year": document.year,
        "entity": document.entity,
        "category": document.category,
        "destination_folder": str(Path("data") / document.category),
        "source_type": "pdf",
        "notes": document.notes,
    }


def add_documents() -> list[tuple[RecommendedDocument, Path, str]]:
    """Download recommended documents and update metadata."""
    ensure_folder_structure()
    rows = read_existing_metadata()
    existing_urls = {row["original_filename"] for row in rows}
    results: list[tuple[RecommendedDocument, Path, str]] = []

    for document in DOCUMENTS:
        destination = DATA_DIR / document.category / document.filename

        if document.url in existing_urls or destination.exists():
            results.append((document, destination, "skipped"))
            continue

        destination = unique_destination_path(destination)
        try:
            download_file(document.url, destination)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            results.append((document, destination, f"failed: {exc}"))
            continue

        rows.append(metadata_row(document, destination.name))
        results.append((document, destination, "downloaded"))

    write_metadata(rows)
    return results


def print_summary(results: list[tuple[RecommendedDocument, Path, str]]) -> None:
    """Print a concise download summary."""
    downloaded = [result for result in results if result[2] == "downloaded"]
    skipped = [result for result in results if result[2] == "skipped"]
    failed = [result for result in results if result[2].startswith("failed")]

    print(f"Downloaded: {len(downloaded)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Failed: {len(failed)}")

    for document, destination, status in results:
        print(f"- {status}: {document.title} -> {destination.relative_to(PROJECT_ROOT)}")

    print(f"\nMetadata CSV: {METADATA_PATH.relative_to(PROJECT_ROOT)}")


def main() -> None:
    """Script entry point."""
    results = add_documents()
    print_summary(results)


if __name__ == "__main__":
    main()
