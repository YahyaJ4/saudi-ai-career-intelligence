"""Organize raw PDF documents into clean RAG source folders.

Run from the project root:
    python scripts/organize_documents.py
"""

from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

try:
    from pypdf import PdfReader
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: pypdf. Install project dependencies with "
        "`pip install -r requirements.txt`, then rerun this script."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
METADATA_PATH = DATA_DIR / "documents_metadata.csv"

DESTINATION_FOLDERS = {
    "vision_reports": DATA_DIR / "vision_reports",
    "strategies": DATA_DIR / "strategies",
    "ai_governance": DATA_DIR / "ai_governance",
    "human_capital": DATA_DIR / "human_capital",
    "sector_programs": DATA_DIR / "sector_programs",
    "job_postings": DATA_DIR / "job_postings",
    "company_profiles": DATA_DIR / "company_profiles",
}

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

ENTITY_PATTERNS = [
    ("vision2030", ["vision 2030", "vision2030"]),
    ("sdaia", ["sdaia", "saudi data & ai authority", "saudi data and ai authority"]),
    ("hcdp", ["human capability development program", "hcdp"]),
    ("mcit", ["ministry of communications and information technology", "mcit"]),
    ("ntdp", ["national technology development program", "ntdp"]),
    ("hrdf", ["human resources development fund", "hrdf", "hadaf"]),
    ("nitaqat", ["nitaqat"]),
    ("gaia", ["global ai summit", "gaia"]),
    ("nca", ["national cybersecurity authority", "nca"]),
    ("ndmo", ["national data management office", "ndmo"]),
    ("pif", ["public investment fund", "pif"]),
    ("monshaat", ["monshaat", "small and medium enterprises general authority"]),
]

CATEGORY_PATTERNS = [
    ("vision_reports", ["vision 2030", "annual report", "vision realization"]),
    ("ai_governance", ["ai ethics", "artificial intelligence ethics", "data governance", "governance", "policy", "regulation"]),
    ("human_capital", ["human capability", "hcdp", "skills", "training", "education", "talent", "labor market"]),
    ("sector_programs", ["program", "sector", "digital economy", "industry", "tourism", "health", "finance"]),
    ("job_postings", ["job posting", "job description", "vacancy", "career", "role", "responsibilities"]),
    ("company_profiles", ["company profile", "about us", "portfolio", "corporate profile"]),
    ("strategies", ["strategy", "strategic", "national strategy", "ict strategy", "digital strategy"]),
]

TITLE_STOPWORDS = {
    "pdf",
    "en",
    "english",
    "final",
    "draft",
    "copy",
    "version",
    "v1",
    "v2",
    "v3",
}


@dataclass
class DocumentInfo:
    """Inferred metadata for one source PDF."""

    original_path: Path
    original_filename: str
    new_filename: str
    title: str
    year: str
    entity: str
    category: str
    destination_folder: str
    source_type: str
    notes: str


def ensure_folder_structure() -> None:
    """Create raw and destination folders if they do not already exist."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for folder in DESTINATION_FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)


def read_first_pages(pdf_path: Path, page_count: int = 3) -> tuple[str, list[str]]:
    """Extract text from the first pages of a PDF, returning text and notes."""
    notes: list[str] = []
    page_text: list[str] = []

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        return "", [f"Could not open PDF: {exc}"]

    total_pages = min(page_count, len(reader.pages))
    for index in range(total_pages):
        try:
            page_text.append(reader.pages[index].extract_text() or "")
        except Exception as exc:
            notes.append(f"Could not read page {index + 1}: {exc}")

    if not page_text:
        notes.append("No text extracted from first pages.")

    return "\n".join(page_text), notes


def normalize_text(value: str) -> str:
    """Normalize text for matching and filename generation."""
    return re.sub(r"\s+", " ", value).strip()


def snake_case(value: str) -> str:
    """Convert a string to compact snake_case."""
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def infer_year(filename: str, text: str) -> str:
    """Infer a likely publication year from filename first, then PDF text."""
    combined = f"{filename}\n{text}"
    years = re.findall(r"\b(20[0-3][0-9])\b", combined)
    return years[0] if years else "unknown_year"


def infer_entity(filename: str, text: str) -> str:
    """Infer publisher or entity using known Saudi strategy source patterns."""
    searchable = f"{filename} {text}".lower()

    for entity, patterns in ENTITY_PATTERNS:
        if any(pattern in searchable for pattern in patterns):
            return entity

    filename_entity = snake_case(Path(filename).stem).split("_")
    return filename_entity[0] if filename_entity else "unknown_entity"


def infer_category(filename: str, text: str) -> str:
    """Infer destination category from filename and first-page content."""
    searchable = f"{filename} {text}".lower()

    for category, patterns in CATEGORY_PATTERNS:
        if any(pattern in searchable for pattern in patterns):
            return category

    return "strategies"


def clean_title_from_filename(filename: str, year: str, entity: str) -> str:
    """Create a human-readable title inspired by the existing filename."""
    stem = Path(filename).stem
    tokens = snake_case(stem).split("_")
    ignored = TITLE_STOPWORDS | {year, entity}
    title_tokens = [token for token in tokens if token and token not in ignored]

    if not title_tokens:
        title_tokens = [token for token in tokens if token]

    return " ".join(title_tokens).title() if title_tokens else "Untitled Document"


def infer_title(filename: str, text: str, year: str, entity: str) -> str:
    """Infer a concise document title from PDF text, falling back to filename."""
    lines = [
        normalize_text(line)
        for line in text.splitlines()
        if 8 <= len(normalize_text(line)) <= 140
    ]

    for line in lines[:12]:
        lower_line = line.lower()
        if "table of contents" in lower_line or "copyright" in lower_line:
            continue
        if re.search(r"[A-Za-z]", line):
            return line

    return clean_title_from_filename(filename, year, entity)


def short_title(title: str, filename: str) -> str:
    """Create a short title segment for the renamed PDF."""
    source = title or clean_title_from_filename(filename, "unknown_year", "unknown_entity")
    words = [
        word
        for word in snake_case(source).split("_")
        if word and word not in TITLE_STOPWORDS
    ]
    return "_".join(words[:6]) or "document"


def short_title_from_filename(filename: str, year: str, entity: str) -> str:
    """Create a filename segment from meaningful words in the original name."""
    tokens = snake_case(Path(filename).stem).split("_")
    ignored = TITLE_STOPWORDS | {year, entity, "unknown", "year", "entity"}
    words = [token for token in tokens if token and token not in ignored]
    return "_".join(words[:6])


def unique_destination_path(destination_folder: Path, filename: str) -> Path:
    """Return a destination path that does not overwrite an existing file."""
    candidate = destination_folder / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    version = 2
    while True:
        versioned = destination_folder / f"{stem}_v{version}{suffix}"
        if not versioned.exists():
            return versioned
        version += 1


def build_document_info(pdf_path: Path) -> DocumentInfo:
    """Read and infer all metadata needed to organize one PDF."""
    text, notes = read_first_pages(pdf_path)
    year = infer_year(pdf_path.name, text)
    entity = infer_entity(pdf_path.name, text)
    category = infer_category(pdf_path.name, text)
    title = infer_title(pdf_path.name, text, year, entity)
    filename_title = short_title_from_filename(pdf_path.name, year, entity) or short_title(
        title,
        pdf_path.name,
    )
    filename = f"{year}_{entity}_{filename_title}.pdf"
    destination_folder = DESTINATION_FOLDERS[category]
    destination_path = unique_destination_path(destination_folder, filename)

    if destination_path.name != filename:
        notes.append("Filename collision resolved with version suffix.")

    return DocumentInfo(
        original_path=pdf_path,
        original_filename=pdf_path.name,
        new_filename=destination_path.name,
        title=title,
        year=year,
        entity=entity,
        category=category,
        destination_folder=str(destination_folder.relative_to(PROJECT_ROOT)),
        source_type="pdf",
        notes="; ".join(notes),
    )


def read_existing_metadata() -> dict[str, dict[str, str]]:
    """Read existing metadata rows keyed by original filename."""
    if not METADATA_PATH.exists():
        return {}

    with METADATA_PATH.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return {
            row.get("original_filename", ""): {column: row.get(column, "") for column in METADATA_COLUMNS}
            for row in reader
        }


def write_metadata(rows: dict[str, dict[str, str]]) -> None:
    """Write metadata rows using a stable column order."""
    with METADATA_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=METADATA_COLUMNS)
        writer.writeheader()
        writer.writerows(rows.values())


def metadata_row(info: DocumentInfo) -> dict[str, str]:
    """Convert inferred document metadata into a CSV row."""
    return {
        "original_filename": info.original_filename,
        "new_filename": info.new_filename,
        "title": info.title,
        "year": info.year,
        "entity": info.entity,
        "category": info.category,
        "destination_folder": info.destination_folder,
        "source_type": info.source_type,
        "notes": info.notes,
    }


def organize_pdf(info: DocumentInfo) -> Path:
    """Move one PDF to its inferred category folder with its new name."""
    destination = PROJECT_ROOT / info.destination_folder / info.new_filename
    shutil.move(str(info.original_path), str(destination))
    return destination


def organize_documents() -> list[tuple[DocumentInfo, Path]]:
    """Organize all PDFs in data/raw_docs and update metadata CSV."""
    ensure_folder_structure()
    metadata_rows = read_existing_metadata()
    organized: list[tuple[DocumentInfo, Path]] = []

    for pdf_path in sorted(RAW_DOCS_DIR.glob("*.pdf")):
        info = build_document_info(pdf_path)
        destination = organize_pdf(info)
        metadata_rows[info.original_filename] = metadata_row(info)
        organized.append((info, destination))

    write_metadata(metadata_rows)
    return organized


def print_summary(organized: list[tuple[DocumentInfo, Path]]) -> None:
    """Print a concise move/rename summary for the user."""
    if not organized:
        print("No PDF files found in data/raw_docs.")
        print(f"Metadata CSV is ready at {METADATA_PATH.relative_to(PROJECT_ROOT)}.")
        return

    print(f"Organized {len(organized)} PDF file(s):")
    for info, destination in organized:
        print(
            f"- {info.original_filename} -> "
            f"{destination.relative_to(PROJECT_ROOT)} "
            f"[{info.category}, {info.entity}, {info.year}]"
        )

    print(f"\nMetadata updated: {METADATA_PATH.relative_to(PROJECT_ROOT)}")


def main() -> None:
    """Script entry point."""
    organized = organize_documents()
    print_summary(organized)


if __name__ == "__main__":
    main()
