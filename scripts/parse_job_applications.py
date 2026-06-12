"""Parse numbered LinkedIn job application postings from a PDF.

Run from the project root:
    python scripts/parse_job_applications.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "data" / "raw_docs" / "linkedin_job_applications_numbered.pdf"
JOB_POSTINGS_DIR = PROJECT_ROOT / "data" / "job_postings"
PROCESSED_DIR = JOB_POSTINGS_DIR / "processed"
RAW_TEXT_DIR = JOB_POSTINGS_DIR / "raw_text"
CSV_PATH = PROCESSED_DIR / "job_postings.csv"
JSON_PATH = PROCESSED_DIR / "job_postings.json"

DESCRIPTION_MARKERS = [
    "Description & Requirements",
    "Description",
    "About the job",
    "About The Role",
    "Job Description",
    "Overview",
]

SECTION_LABELS = [
    "Key Responsibilities",
    "Responsibilities",
    "What You'll Do",
    "What You’ll Do",
    "Requirements",
    "Qualifications",
    "Minimum Qualifications",
    "Preferred Qualifications",
    "About You",
    "Benefits",
    "Compensation",
    "Nice to Have",
]

CATEGORY_KEYWORDS = {
    "GDP": ["gdp", "vision 2030", "economic growth", "pif", "public investment fund"],
    "AI Engineering": [
        "ai engineer",
        "ai developer",
        "machine learning engineer",
        "ml engineer",
        "model deployment",
        "mlops",
    ],
    "Data Science": ["data scientist", "data science", "machine learning", "analytics", "statistical"],
    "Consulting": ["consultant", "consulting", "advisory", "strategy", "client"],
    "Software Engineering": ["software engineer", "backend", "frontend", "full stack", "api"],
    "Government": ["government", "public sector", "ministry", "authority", "regulator"],
    "Fintech": ["fintech", "fin-tech", "finance", "financial", "payments", "banking"],
    "Computer Vision": ["computer vision", "opencv", "image processing", "object detection"],
    "GenAI / LLM": ["generative ai", "genai", "llm", "large language model", "rag", "langchain", "openai"],
    "Business Intelligence": ["business intelligence", "power bi", "tableau", "dashboard", "reporting"],
    "Research": ["research", "researcher", "scientist", "experiment", "prototype"],
}

SECTOR_KEYWORDS = {
    "Fintech": ["fintech", "fin-tech", "finance", "financial", "bank", "payment", "expense"],
    "Government": ["government", "public sector", "ministry", "authority", "municipality", "national"],
    "Consulting": ["consulting", "consultancy", "consultant", "advisory", "bain"],
    "Telecom": ["telecom", "telecommunications", "5g", "stc", "zain", "mobily"],
    "Real Estate": ["real estate", "property", "construction", "rer", "السجل العقاري"],
    "Investment": ["investment", "venture", "private equity", "asset management", "pif"],
    "Logistics": ["logistics", "supply chain", "shipping", "warehouse", "ninja"],
    "Gaming": ["gaming", "game", "esports", "unity", "unreal"],
    "Healthcare": ["healthcare", "hospital", "clinical", "medical", "patient"],
    "Technology": ["technology", "software", "cloud", "ai", "data", "platform", "saas", "systems"],
    "Energy": ["energy", "oil", "gas", "renewable", "solar", "aramco"],
}

ROLE_PATTERNS = [
    r"associate consultant(?:\s*-\s*[a-z0-9 /&()+#.-]+)?",
    r"artificial intelligence engineer",
    r"ai agent engineer",
    r"ai developer",
    r"ai engineer",
    r"ai research engineer(?:\s*-\s*[a-z ]+)?",
    r"analytics engineer",
    r"backend engineer",
    r"business analyst",
    r"business intelligence analyst",
    r"computer vision engineer",
    r"consultant",
    r"data analyst",
    r"data engineer",
    r"data scientist",
    r"full stack engineer",
    r"gen\s+ai engineer",
    r"graduate programme",
    r"machine learning engineer",
    r"ml engineer",
    r"pre-sales engineer",
    r"presales engineer",
    r"product manager",
    r"research scientist",
    r"software developer",
    r"software engineer",
]

SKILL_TOOL_KEYWORDS = [
    "AI",
    "API Development",
    "AWS",
    "Azure",
    "Business Analysis",
    "Computer Vision",
    "Data Analysis",
    "Data Engineering",
    "Data Science",
    "Deep Learning",
    "Docker",
    "FastAPI",
    "Generative AI",
    "Kubernetes",
    "LangChain",
    "LLMs",
    "Machine Learning",
    "MLOps",
    "NLP",
    "OpenAI",
    "Pandas",
    "Power BI",
    "Prompt Engineering",
    "PyTorch",
    "RAG",
    "Research",
    "SAP",
    "SQL",
    "Tableau",
    "TensorFlow",
]

OUTPUT_COLUMNS = [
    "job_number",
    "raw_title",
    "company",
    "role_title",
    "location",
    "description",
    "requirements",
    "responsibilities",
    "skills_tools",
    "salary_if_available",
    "experience_required",
    "category",
    "sector",
]


@dataclass
class HeadingMatch:
    """A numbered job heading found in the PDF text."""

    start: int
    end: int
    job_number: int
    raw_title: str


@dataclass
class JobPosting:
    """Structured job posting fields."""

    job_number: int
    raw_title: str
    company: str
    role_title: str
    location: str
    description: str
    requirements: str
    responsibilities: str
    skills_tools: list[str]
    salary_if_available: str
    experience_required: str
    category: str
    sector: str


def ensure_directories() -> None:
    """Create output directories."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_TEXT_DIR.mkdir(parents=True, exist_ok=True)


def clean_value(value: str) -> str:
    """Normalize whitespace and trim noisy punctuation."""
    replacements = {
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "Â£": "£",
        "â‚¬": "€",
    }
    for bad, good in replacements.items():
        value = value.replace(bad, good)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t\r\n-|:;,")


def read_pdf_text(path: Path) -> str:
    """Extract text from the input PDF using pypdf."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input PDF: {path.relative_to(PROJECT_ROOT)}. "
            "Expected data/raw_docs/linkedin_job_applications_numbered.pdf."
        )

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    text = text.replace("\u00a0", " ")
    text = clean_value(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def flow_text(text: str) -> str:
    """Collapse PDF text to a single searchable stream without using page numbers."""
    return re.sub(r"\s+", " ", text).strip()


def description_marker_pattern() -> str:
    """Build a regex fragment for common job-body markers."""
    return "|".join(re.escape(marker) for marker in DESCRIPTION_MARKERS)


def find_prefix_headings(text: str) -> list[HeadingMatch]:
    """Find headings like '15. Company' or '1. Associate Consultant - SAP'."""
    marker = description_marker_pattern()
    pattern = re.compile(
        rf"(?<!\d)(?P<number>\d{{1,4}})\.\s+"
        rf"(?P<title>.{{2,180}}?)"
        rf"(?=\s+(?:{marker})\b)",
        re.IGNORECASE,
    )
    matches = []
    for match in pattern.finditer(text):
        title = clean_value(match.group("title"))
        if title:
            matches.append(
                HeadingMatch(
                    start=match.start(),
                    end=match.end(),
                    job_number=int(match.group("number")),
                    raw_title=title,
                )
            )
    return matches


def find_trailing_number_headings(text: str) -> list[HeadingMatch]:
    """Find headings like 'السجل العقاري | RER 15.' or 'نينجا Ninja 23.'."""
    marker = description_marker_pattern()
    pattern = re.compile(
        rf"(?P<title>(?:[\w\u0600-\u06ff|&().,'+/#-]+\s+){{1,14}})"
        rf"(?P<number>\d{{1,4}})\."
        rf"(?=\s+(?:{marker})\b)",
        re.IGNORECASE,
    )
    matches = []
    for match in pattern.finditer(text):
        title = clean_value(match.group("title"))
        if title and not re.match(r"^\d+\.", title):
            matches.append(
                HeadingMatch(
                    start=match.start(),
                    end=match.end(),
                    job_number=int(match.group("number")),
                    raw_title=title,
                )
            )
    return matches


def remove_overlapping_matches(matches: list[HeadingMatch]) -> list[HeadingMatch]:
    """Keep one heading per text span, preferring the earlier and longer match."""
    selected: list[HeadingMatch] = []
    for match in sorted(matches, key=lambda item: (item.start, -(item.end - item.start))):
        if selected and match.start < selected[-1].end:
            continue
        selected.append(match)
    return selected


def split_job_records(text: str) -> list[tuple[HeadingMatch, str]]:
    """Split each numbered job heading into its own record."""
    compact = flow_text(text)
    headings = remove_overlapping_matches(
        find_prefix_headings(compact) + find_trailing_number_headings(compact)
    )

    records = []
    for index, heading in enumerate(headings):
        next_start = headings[index + 1].start if index + 1 < len(headings) else len(compact)
        records.append((heading, compact[heading.start:next_start].strip()))
    return records


def text_after_heading(record: str, heading: HeadingMatch) -> str:
    """Remove the numbered heading from a record."""
    return record[heading.end - heading.start :].strip()


def extract_section(text: str, starts: list[str], stops: list[str]) -> str:
    """Extract text after a section label until the next known section label."""
    start_pattern = "|".join(re.escape(label) for label in starts)
    stop_pattern = "|".join(re.escape(label) for label in stops)
    label_prefix = r"(?<![A-Za-z])"
    label_suffix = r"(?=\s+[A-Z0-9]|\s*$|:)"
    match = re.search(rf"{label_prefix}(?:{start_pattern}){label_suffix}", text, re.IGNORECASE)
    if not match:
        return ""

    section_start = match.end()
    stop_match = re.search(
        rf"{label_prefix}(?:{stop_pattern}){label_suffix}",
        text[section_start:],
        re.IGNORECASE,
    )
    section_end = section_start + stop_match.start() if stop_match else len(text)
    return clean_value(text[section_start:section_end])


def extract_description(body: str) -> str:
    """Extract the main description before responsibilities or requirements sections."""
    marker = description_marker_pattern()
    body = re.sub(rf"^(?:{marker})\b\s*", "", body, flags=re.IGNORECASE)
    stop_labels = [label for label in SECTION_LABELS if label.lower() not in {"overview"}]
    stop_pattern = "|".join(re.escape(label) for label in stop_labels)
    stop_match = re.search(rf"(?<![A-Za-z])(?:{stop_pattern})(?=\s+[A-Z0-9]|\s*$|:)", body, re.IGNORECASE)
    description = body[: stop_match.start()] if stop_match else body
    return clean_value(description)


def extract_responsibilities(body: str) -> str:
    """Extract responsibilities-oriented text."""
    return extract_section(
        body,
        ["Key Responsibilities", "Responsibilities", "What You'll Do", "What You’ll Do"],
        ["Requirements", "Qualifications", "Minimum Qualifications", "Preferred Qualifications", "About You", "Benefits", "Compensation", "Nice to Have"],
    )


def extract_requirements(body: str) -> str:
    """Extract requirements and qualifications text."""
    return extract_section(
        body,
        ["Requirements", "Qualifications", "Minimum Qualifications", "About You"],
        ["Benefits", "Compensation", "Nice to Have", "Why", "About Us"],
    )


def infer_company_role(raw_title: str, body: str) -> tuple[str, str]:
    """Infer company and role, falling back to raw_title when ambiguous."""
    title = clean_value(raw_title)

    if re.search(r"\bat\b", title, re.IGNORECASE):
        role, company = re.split(r"\bat\b", title, maxsplit=1, flags=re.IGNORECASE)
        return clean_value(company), clean_value(role)

    lower = title.lower()
    role_matches = []
    for role_pattern in ROLE_PATTERNS:
        match = re.search(rf"\b{role_pattern}\b", lower, re.IGNORECASE)
        if match:
            role_matches.append(match)

    if role_matches:
        match = sorted(role_matches, key=lambda item: item.start())[0]
        if match.start() == 0:
            role = clean_value(title[: match.end()])
            company = clean_value(title[match.end() :])
        else:
            company = clean_value(title[: match.start()])
            role = clean_value(title[match.start() : match.end()])
        return company, role

    body_role = re.search(
        r"\b(?:looking for|seeking|hiring)\s+(?:an?|the)?\s*([A-Za-z0-9/&().,+#\-\s]{3,90}?)(?:\s+to\s+|\s+who\s+|\.|,)",
        body,
        re.IGNORECASE,
    )
    if body_role:
        role = re.sub(r"^(?:talented|experienced|skilled|strong|senior)\s+", "", body_role.group(1), flags=re.IGNORECASE)
        return title, clean_value(role)

    return title, ""


def keyword_matches(text: str, keywords: list[str]) -> list[str]:
    """Find unique keyword hits."""
    matches = []
    for keyword in keywords:
        pattern = re.escape(keyword).replace(r"\ ", r"\s+")
        if re.search(rf"(?<![A-Za-z0-9]){pattern}(?![A-Za-z0-9])", text, re.IGNORECASE):
            matches.append(keyword)
    return matches


def infer_from_keyword_map(text: str, keyword_map: dict[str, list[str]], default: str) -> str:
    """Choose the highest-scoring category or sector from keyword hits."""
    scores: Counter[str] = Counter()
    lower = text.lower()
    for label, keywords in keyword_map.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword.lower())}\b", lower):
                scores[label] += 1
    return scores.most_common(1)[0][0] if scores else default


def extract_location(text: str) -> str:
    """Extract common job locations and work modes."""
    locations = []
    patterns = [
        r"\b(?:Location|Work Location|Based in)\s*[:\-]\s*([A-Za-z\u0600-\u06ff ,/()'-]{2,90})",
        r"\b(Riyadh|Jeddah|Dammam|Khobar|Dhahran|NEOM|Saudi Arabia|KSA|Dubai|Abu Dhabi|Remote|Hybrid|On-site|Montreal|United States)\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = clean_value(match.group(1))
            if value and value.lower() not in {location.lower() for location in locations}:
                locations.append(value)
    return "; ".join(locations[:4])


def extract_salary(text: str) -> str:
    """Extract salary or compensation when an explicit amount is present."""
    patterns = [
        r"((?:SAR|USD|\$|€|£)\s?[\d,]+(?:\s?[-–]\s?(?:SAR|USD|\$|€|£)?\s?[\d,]+)?(?:\s?(?:per|/)\s?(?:year|month|hour|annum))?)",
        r"((?:annualized\s+)?base compensation[^.]{0,160}?(?:SAR|USD|\$|€|£)?\s?[\d,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return clean_value(match.group(1))
    return ""


def extract_experience(text: str) -> str:
    """Extract years or seniority requirements."""
    match = re.search(
        r"\b((?:fresh graduate|entry[- ]level)|(?:up to\s+)?\d+\+?\s*(?:-|to)?\s*\d*\+?\s*years?'?\s+(?:of\s+)?experience)\b",
        text,
        re.IGNORECASE,
    )
    if match:
        return clean_value(match.group(1))

    for label, pattern in {
        "Internship": r"\bintern(ship)?\b",
        "Entry level": r"\b(entry[- ]level|fresh graduate|junior|associate)\b",
        "Mid level": r"\b(mid[- ]level|experienced|specialist)\b",
        "Senior": r"\b(senior|lead|principal|staff)\b",
        "Manager": r"\b(manager|director|head of)\b",
    }.items():
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return ""


def build_job(heading: HeadingMatch, record: str) -> JobPosting:
    """Create a structured job from one numbered section."""
    body = text_after_heading(record, heading)
    company, role = infer_company_role(heading.raw_title, body)
    combined = f"{heading.raw_title} {body}"

    return JobPosting(
        job_number=heading.job_number,
        raw_title=heading.raw_title,
        company=company,
        role_title=role,
        location=extract_location(combined),
        description=extract_description(body),
        requirements=extract_requirements(body),
        responsibilities=extract_responsibilities(body),
        skills_tools=keyword_matches(combined, SKILL_TOOL_KEYWORDS),
        salary_if_available=extract_salary(combined),
        experience_required=extract_experience(combined),
        category=infer_from_keyword_map(combined, CATEGORY_KEYWORDS, "Technology"),
        sector=infer_from_keyword_map(combined, SECTOR_KEYWORDS, "Technology"),
    )


def write_raw_text(records: list[tuple[HeadingMatch, str]]) -> None:
    """Write each numbered section as raw text."""
    for old_file in RAW_TEXT_DIR.glob("job_*.txt"):
        old_file.unlink()

    for heading, record in records:
        path = RAW_TEXT_DIR / f"job_{heading.job_number:03d}.txt"
        path.write_text(record, encoding="utf-8")


def write_outputs(jobs: list[JobPosting]) -> None:
    """Write requested CSV and JSON outputs."""
    csv_rows = []
    json_rows = []
    for job in jobs:
        row = asdict(job)
        json_rows.append(row)
        row_for_csv = row.copy()
        row_for_csv["skills_tools"] = "; ".join(job.skills_tools)
        csv_rows.append(row_for_csv)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(csv_rows)

    with JSON_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(json_rows, json_file, ensure_ascii=False, indent=2)


def validation_report(jobs: list[JobPosting]) -> tuple[list[int], list[int]]:
    """Compute missing and duplicate numbered job ids."""
    numbers = [job.job_number for job in jobs]
    duplicates = [number for number, count in Counter(numbers).items() if count > 1]
    missing = []
    if numbers:
        seen = set(numbers)
        missing = [number for number in range(min(numbers), max(numbers) + 1) if number not in seen]
    return missing, sorted(duplicates)


def print_validation(jobs: list[JobPosting]) -> None:
    """Print required validation details."""
    missing, duplicates = validation_report(jobs)

    print("Job Application Parser")
    print("=" * 30)
    print(f"Input PDF: {PDF_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Total number of jobs detected: {len(jobs)}")
    print(f"Missing job numbers: {missing if missing else 'none'}")
    print(f"Duplicate job numbers: {duplicates if duplicates else 'none'}")
    print("First 5 extracted titles:")
    for job in jobs[:5]:
        title = job.role_title or job.raw_title
        print(f"  {job.job_number}. {title} [{job.raw_title}]")
    print(f"CSV output: {CSV_PATH.relative_to(PROJECT_ROOT)}")
    print(f"JSON output: {JSON_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Raw text output: {RAW_TEXT_DIR.relative_to(PROJECT_ROOT)}")


def parse_job_applications() -> list[JobPosting]:
    """Run the full numbered-heading extraction pipeline."""
    ensure_directories()
    text = read_pdf_text(PDF_PATH)
    records = split_job_records(text)
    jobs = [build_job(heading, record) for heading, record in records]

    write_raw_text(records)
    write_outputs(jobs)
    print_validation(jobs)
    return jobs


def main() -> None:
    """Script entry point."""
    parse_job_applications()


if __name__ == "__main__":
    main()
