"""Organize raw job posting text files into clean filenames and metadata.

Run from the project root:
    python scripts/organize_job_postings.py
"""

from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOB_POSTINGS_DIR = PROJECT_ROOT / "data" / "job_postings"
RAW_DIR = JOB_POSTINGS_DIR / "raw"
METADATA_PATH = JOB_POSTINGS_DIR / "job_postings_metadata.csv"

METADATA_COLUMNS = [
    "original_filename",
    "new_filename",
    "company",
    "role",
    "date",
    "location",
    "employment_type",
    "seniority",
    "skills",
    "source",
    "notes",
]

FIELD_PATTERNS = {
    "company": [
        r"(?im)^\s*(?:company|employer|organization|organisation)\s*[:\-]\s*(.+)$",
        r"(?im)^\s*(?:at|by)\s+(.+)$",
    ],
    "role": [
        r"(?im)^\s*(?:role|title|job title|position)\s*[:\-]\s*(.+)$",
        r"(?im)^\s*(?:hiring|we are hiring)\s*[:\-]\s*(.+)$",
    ],
    "date": [
        r"(?im)^\s*(?:date posted|posted|posting date|published|date)\s*[:\-]\s*(.+)$",
        r"\b(20[0-3][0-9][-/\.](?:0?[1-9]|1[0-2])[-/\.](?:0?[1-9]|[12][0-9]|3[01]))\b",
    ],
    "location": [
        r"(?im)^\s*(?:location|city|work location)\s*[:\-]\s*(.+)$",
    ],
    "employment_type": [
        r"(?im)^\s*(?:employment type|job type|type)\s*[:\-]\s*(.+)$",
    ],
    "seniority": [
        r"(?im)^\s*(?:seniority|level|experience level)\s*[:\-]\s*(.+)$",
    ],
    "source": [
        r"(?im)^\s*(?:source|url|link)\s*[:\-]\s*(.+)$",
    ],
}

SKILL_KEYWORDS = [
    "ai",
    "analytics",
    "api",
    "aws",
    "azure",
    "cloud",
    "computer vision",
    "data analysis",
    "data engineering",
    "data science",
    "deep learning",
    "docker",
    "etl",
    "generative ai",
    "git",
    "llm",
    "machine learning",
    "mlops",
    "nlp",
    "power bi",
    "python",
    "pytorch",
    "rag",
    "sql",
    "tensorflow",
]


@dataclass
class JobPostingMetadata:
    """Structured metadata extracted from one raw job posting."""

    original_path: Path
    original_filename: str
    new_filename: str
    company: str
    role: str
    date: str
    location: str
    employment_type: str
    seniority: str
    skills: str
    source: str
    notes: str


def ensure_folder_structure() -> None:
    """Create required job posting folders."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    JOB_POSTINGS_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    """Read a raw job posting text file."""
    return path.read_text(encoding="utf-8", errors="replace")


def clean_value(value: str) -> str:
    """Trim a captured metadata field."""
    return re.sub(r"\s+", " ", value).strip(" \t\r\n-|")


def extract_field(text: str, field: str) -> str:
    """Extract a structured field using label-based patterns."""
    for pattern in FIELD_PATTERNS.get(field, []):
        match = re.search(pattern, text)
        if match:
            return clean_value(match.group(1))
    return ""


def infer_role_from_text(text: str, filename: str) -> str:
    """Infer role from labeled fields, heading lines, then filename."""
    role = extract_field(text, "role")
    if role:
        return role

    for line in text.splitlines()[:8]:
        clean_line = clean_value(line)
        if 4 <= len(clean_line) <= 90 and re.search(r"[A-Za-z]", clean_line):
            return clean_line

    return Path(filename).stem.replace("_", " ").replace("-", " ").title()


def infer_company_from_text(text: str, filename: str) -> str:
    """Infer company from labeled fields or filename prefix."""
    company = extract_field(text, "company")
    if company:
        return company

    stem_parts = re.split(r"[_\-]+", Path(filename).stem)
    if len(stem_parts) >= 2:
        return stem_parts[0].title()

    return "unknown_company"


def normalize_date(value: str) -> str:
    """Normalize a date value to YYYY-MM-DD where possible."""
    if not value:
        return date.today().isoformat()

    value = clean_value(value)
    numeric = re.search(
        r"\b(20[0-3][0-9])[-/\.](0?[1-9]|1[0-2])[-/\.](0?[1-9]|[12][0-9]|3[01])\b",
        value,
    )
    if numeric:
        year, month, day = numeric.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    month_match = re.search(
        r"(?i)\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
        r"dec(?:ember)?)\s+([0-3]?[0-9]),?\s+(20[0-3][0-9])\b",
        value,
    )
    if month_match:
        month_name, day, year = month_match.groups()
        month_number = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }[month_name[:3].lower()]
        return f"{year}-{month_number:02d}-{int(day):02d}"

    year_match = re.search(r"\b(20[0-3][0-9])\b", value)
    if year_match:
        return f"{year_match.group(1)}-01-01"

    return date.today().isoformat()


def infer_date(text: str) -> str:
    """Infer posting date, defaulting to today's date when missing."""
    return normalize_date(extract_field(text, "date"))


def extract_skills(text: str) -> str:
    """Extract known skill keywords from the posting text."""
    searchable = text.lower()
    skills = [
        skill
        for skill in SKILL_KEYWORDS
        if re.search(rf"\b{re.escape(skill)}\b", searchable)
    ]
    return "; ".join(skills)


def snake_case(value: str) -> str:
    """Convert a value to snake_case for filenames."""
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def unique_destination_path(filename: str) -> Path:
    """Return a destination filename that does not overwrite an existing file."""
    destination = JOB_POSTINGS_DIR / filename
    if not destination.exists():
        return destination

    version = 2
    while True:
        candidate = JOB_POSTINGS_DIR / f"{destination.stem}_v{version}{destination.suffix}"
        if not candidate.exists():
            return candidate
        version += 1


def build_metadata(path: Path) -> JobPostingMetadata:
    """Extract metadata and construct the new filename for a raw posting."""
    text = read_text(path)
    company = infer_company_from_text(text, path.name)
    role = infer_role_from_text(text, path.name)
    posted_date = infer_date(text)
    location = extract_field(text, "location")
    employment_type = extract_field(text, "employment_type")
    seniority = extract_field(text, "seniority")
    source = extract_field(text, "source")
    skills = extract_skills(text)

    filename = f"{snake_case(company)}_{snake_case(role)}_{posted_date}.txt"
    destination = unique_destination_path(filename)
    notes = []
    if company == "unknown_company":
        notes.append("Company not found; used fallback.")
    if not extract_field(text, "date"):
        notes.append("Posting date not found; used today's date.")
    if destination.name != filename:
        notes.append("Filename collision resolved with version suffix.")

    return JobPostingMetadata(
        original_path=path,
        original_filename=path.name,
        new_filename=destination.name,
        company=company,
        role=role,
        date=posted_date,
        location=location,
        employment_type=employment_type,
        seniority=seniority,
        skills=skills,
        source=source,
        notes="; ".join(notes),
    )


def read_existing_metadata() -> dict[str, dict[str, str]]:
    """Load existing metadata keyed by original filename."""
    if not METADATA_PATH.exists():
        return {}

    with METADATA_PATH.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return {
            row.get("original_filename", ""): {
                column: row.get(column, "") for column in METADATA_COLUMNS
            }
            for row in reader
        }


def write_metadata(rows: dict[str, dict[str, str]]) -> None:
    """Write the job posting metadata CSV."""
    with METADATA_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows.values())


def metadata_row(metadata: JobPostingMetadata) -> dict[str, str]:
    """Convert metadata to a CSV row."""
    return {
        "original_filename": metadata.original_filename,
        "new_filename": metadata.new_filename,
        "company": metadata.company,
        "role": metadata.role,
        "date": metadata.date,
        "location": metadata.location,
        "employment_type": metadata.employment_type,
        "seniority": metadata.seniority,
        "skills": metadata.skills,
        "source": metadata.source,
        "notes": metadata.notes,
    }


def organize_posting(metadata: JobPostingMetadata) -> Path:
    """Move a raw posting to its clean destination filename."""
    destination = JOB_POSTINGS_DIR / metadata.new_filename
    shutil.move(str(metadata.original_path), str(destination))
    return destination


def organize_job_postings() -> list[tuple[JobPostingMetadata, Path]]:
    """Organize all raw job posting text files and update metadata."""
    ensure_folder_structure()
    rows = read_existing_metadata()
    organized: list[tuple[JobPostingMetadata, Path]] = []

    for path in sorted(RAW_DIR.glob("*.txt")):
        metadata = build_metadata(path)
        destination = organize_posting(metadata)
        rows[metadata.original_filename] = metadata_row(metadata)
        organized.append((metadata, destination))

    write_metadata(rows)
    return organized


def print_summary(organized: list[tuple[JobPostingMetadata, Path]]) -> None:
    """Print a clear rename/move summary."""
    if not organized:
        print("No raw job posting .txt files found in data/job_postings/raw.")
        print(f"Metadata CSV is ready at {METADATA_PATH.relative_to(PROJECT_ROOT)}.")
        return

    print(f"Organized {len(organized)} job posting file(s):")
    for metadata, destination in organized:
        print(
            f"- {metadata.original_filename} -> "
            f"{destination.relative_to(PROJECT_ROOT)} "
            f"[{metadata.company} | {metadata.role} | {metadata.date}]"
        )

    print(f"\nMetadata updated: {METADATA_PATH.relative_to(PROJECT_ROOT)}")


def main() -> None:
    """Script entry point."""
    organized = organize_job_postings()
    print_summary(organized)


if __name__ == "__main__":
    main()
