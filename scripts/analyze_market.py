"""Generate Power BI-ready market analysis files from parsed job postings.

Run from the project root:
    python scripts/analyze_market.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "job_postings" / "processed" / "job_postings.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "market_analysis"
POWERBI_DIR = OUTPUT_DIR / "powerbi"

KNOWN_STRENGTHS = {
    "Python",
    "PyTorch",
    "RAG",
    "Machine Learning",
    "Data Science",
    "Research",
    "Data Analysis",
}

GROWTH_TARGETS = {
    "LangChain",
    "Docker",
    "Power BI",
    "SQL",
    "FastAPI",
    "MLOps",
    "AWS",
    "Azure",
}

TOOLS = {
    "AWS",
    "Azure",
    "Chroma",
    "CUDA",
    "Docker",
    "FastAPI",
    "Git",
    "Kubernetes",
    "LangChain",
    "LLMs",
    "MLOps",
    "NumPy",
    "OpenAI",
    "Pandas",
    "Power BI",
    "PyTorch",
    "RAG",
    "SAP",
    "SQL",
    "Streamlit",
    "Tableau",
    "TensorFlow",
}

SKILL_ALIASES = {
    "AI": "Artificial Intelligence",
    "LLMs": "Large Language Models",
}

LOCATION_KEYWORDS = [
    "Riyadh",
    "Jeddah",
    "Dammam",
    "Khobar",
    "Dhahran",
    "NEOM",
    "Saudi Arabia",
    "KSA",
    "Dubai",
    "Abu Dhabi",
    "Remote",
    "Hybrid",
    "On-site",
    "Montreal",
    "United States",
]

CSV_COLUMNS = {
    "jobs": [
        "job_number",
        "raw_title",
        "company",
        "role_title",
        "category",
        "sector",
        "location",
        "seniority_level",
        "experience_required",
        "salary_if_available",
        "skills_tools_count",
        "has_salary",
        "has_location",
    ],
    "frequency": ["name", "count", "percentage"],
    "job_skill_bridge": ["job_number", "skill_tool", "type", "is_known_strength", "is_growth_target"],
    "location_bridge": ["job_number", "location"],
    "recommendations": [
        "recommendation_id",
        "project",
        "priority",
        "market_gap",
        "target_roles",
        "skills_tools_to_show",
        "suggested_artifact",
    ],
}


def ensure_output_dir() -> None:
    """Create output folders."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(value: str | None) -> str:
    """Clean text values and repair common terminal/PDF encoding artifacts."""
    if not value:
        return ""
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
    return re.sub(r"\s+", " ", value).strip()


def read_jobs() -> list[dict[str, str]]:
    """Read parsed job postings."""
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input dataset: {INPUT_CSV.relative_to(PROJECT_ROOT)}")

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            {key: clean_text(value) for key, value in row.items()}
            for row in reader
        ]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write rows to CSV with stable columns."""
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def percentage(count: int, total: int) -> str:
    """Format percentage for BI labels."""
    if total == 0:
        return "0.00"
    return f"{(count / total) * 100:.2f}"


def split_items(value: str) -> list[str]:
    """Split semicolon-delimited skills/tools."""
    items = []
    for item in value.split(";"):
        clean_item = clean_text(item)
        if clean_item:
            items.append(SKILL_ALIASES.get(clean_item, clean_item))
    return items


def item_type(item: str) -> str:
    """Classify an item as skill or tool/technology."""
    return "tool_technology" if item in TOOLS else "skill"


def normalize_company(row: dict[str, str]) -> str:
    """Use raw title when company extraction was blank."""
    return row.get("company") or row.get("raw_title") or "Unknown"


def normalize_seniority(value: str) -> str:
    """Normalize experience strings into dashboard-friendly seniority buckets."""
    text = value.lower()
    if not text:
        return "Not specified"
    if "intern" in text:
        return "Internship"
    if "fresh" in text or "entry" in text or "0+" in text or "junior" in text:
        return "Entry / Fresh Graduate"
    if re.search(r"\b[12]\+?\s*(?:-|to)?\s*\d*\+?\s*years?", text):
        return "Junior / Early Career"
    if re.search(r"\b[34]\+?\s*(?:-|to)?\s*\d*\+?\s*years?", text) or "mid" in text:
        return "Mid Level"
    if re.search(r"\b[5-9]\+?\s*(?:-|to)?\s*\d*\+?\s*years?", text) or "senior" in text:
        return "Senior"
    if "manager" in text or "director" in text or "head of" in text:
        return "Manager / Lead"
    return clean_text(value)


def locations_for_job(row: dict[str, str]) -> list[str]:
    """Extract normalized locations from explicit location and posting text."""
    haystack = " ".join(
        [
            row.get("location", ""),
            row.get("raw_title", ""),
            row.get("description", ""),
            row.get("requirements", ""),
            row.get("responsibilities", ""),
        ]
    )
    found = []
    for location in LOCATION_KEYWORDS:
        if re.search(rf"(?<![A-Za-z]){re.escape(location)}(?![A-Za-z])", haystack, re.IGNORECASE):
            found.append("Saudi Arabia" if location == "KSA" else location)
    if not found and not row.get("location"):
        found.append("Not specified")
    return sorted(set(found))


def frequency_rows(counter: Counter[str], total: int, name_key: str = "name") -> list[dict[str, object]]:
    """Convert a counter into frequency rows."""
    return [
        {name_key: name, "count": count, "percentage": percentage(count, total)}
        for name, count in counter.most_common()
    ]


def build_powerbi_tables(jobs: list[dict[str, str]]) -> dict[str, list[dict[str, object]]]:
    """Build dashboard-ready tables."""
    total_jobs = len(jobs)
    category_counter: Counter[str] = Counter()
    sector_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    seniority_counter: Counter[str] = Counter()
    location_counter: Counter[str] = Counter()
    skill_counter: Counter[str] = Counter()
    tool_counter: Counter[str] = Counter()

    clean_jobs = []
    job_skill_bridge = []
    location_bridge = []

    for row in jobs:
        job_number = row.get("job_number", "")
        items = split_items(row.get("skills_tools", ""))
        company = normalize_company(row)
        category = row.get("category") or "Uncategorized"
        sector = row.get("sector") or "Unspecified"
        seniority = normalize_seniority(row.get("experience_required", ""))
        locations = locations_for_job(row)

        category_counter[category] += 1
        sector_counter[sector] += 1
        company_counter[company] += 1
        seniority_counter[seniority] += 1

        for location in locations:
            location_counter[location] += 1
            location_bridge.append({"job_number": job_number, "location": location})

        for item in items:
            kind = item_type(item)
            if kind == "tool_technology":
                tool_counter[item] += 1
            else:
                skill_counter[item] += 1
            job_skill_bridge.append(
                {
                    "job_number": job_number,
                    "skill_tool": item,
                    "type": kind,
                    "is_known_strength": item in KNOWN_STRENGTHS,
                    "is_growth_target": item in GROWTH_TARGETS,
                }
            )

        clean_jobs.append(
            {
                "job_number": job_number,
                "raw_title": row.get("raw_title", ""),
                "company": company,
                "role_title": row.get("role_title") or row.get("raw_title", ""),
                "category": category,
                "sector": sector,
                "location": "; ".join(locations),
                "seniority_level": seniority,
                "experience_required": row.get("experience_required", ""),
                "salary_if_available": row.get("salary_if_available", ""),
                "skills_tools_count": len(items),
                "has_salary": bool(row.get("salary_if_available", "")),
                "has_location": locations != ["Not specified"],
            }
        )

    return {
        "jobs_powerbi": clean_jobs,
        "role_category_breakdown": frequency_rows(category_counter, total_jobs, "category"),
        "sector_breakdown": frequency_rows(sector_counter, total_jobs, "sector"),
        "company_breakdown": frequency_rows(company_counter, total_jobs, "company"),
        "seniority_breakdown": frequency_rows(seniority_counter, total_jobs, "seniority_level"),
        "location_distribution": frequency_rows(location_counter, total_jobs, "location"),
        "top_skills_requested": frequency_rows(skill_counter, total_jobs, "skill"),
        "top_tools_technologies": frequency_rows(tool_counter, total_jobs, "tool_technology"),
        "job_skill_tool_bridge": job_skill_bridge,
        "job_location_bridge": location_bridge,
    }


def build_recommendations(tables: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    """Build portfolio project recommendations from market gaps."""
    return [
        {
            "recommendation_id": 1,
            "project": "Saudi AI Job Market Dashboard",
            "priority": "High",
            "market_gap": "Power BI, SQL, and analytics storytelling need stronger portfolio evidence.",
            "target_roles": "Data Scientist; Data Engineer; AI Consultant; Business Intelligence",
            "skills_tools_to_show": "Power BI; SQL; Data Analysis; dashboard design; market insights",
            "suggested_artifact": "Power BI dashboard using role, skill, sector, location, and seniority CSVs.",
        },
        {
            "recommendation_id": 2,
            "project": "Fintech RAG Analyst",
            "priority": "High",
            "market_gap": "RAG and LLM demand is visible, while LangChain and Docker need stronger evidence.",
            "target_roles": "AI Engineer; GenAI Engineer; Fintech AI Engineer",
            "skills_tools_to_show": "LangChain; RAG; Chroma; Docker; Streamlit; source citations",
            "suggested_artifact": "Question-answer app over fintech reports with citations and Docker setup.",
        },
        {
            "recommendation_id": 3,
            "project": "ML Prediction API with Docker",
            "priority": "Medium",
            "market_gap": "AI/data roles often ask for deployment readiness and reproducible ML workflows.",
            "target_roles": "Data Scientist; ML Engineer; AI Engineer",
            "skills_tools_to_show": "FastAPI; Docker; model evaluation; Python; MLOps basics",
            "suggested_artifact": "API service around an ML model with metrics, model card, and Dockerfile.",
        },
    ]


def write_outputs(tables: dict[str, list[dict[str, object]]], recommendations: list[dict[str, object]]) -> None:
    """Write BI-ready CSV outputs and a manifest."""
    write_csv(POWERBI_DIR / "jobs_powerbi.csv", tables["jobs_powerbi"], CSV_COLUMNS["jobs"])
    write_csv(POWERBI_DIR / "role_category_breakdown.csv", tables["role_category_breakdown"], ["category", "count", "percentage"])
    write_csv(POWERBI_DIR / "sector_breakdown.csv", tables["sector_breakdown"], ["sector", "count", "percentage"])
    write_csv(POWERBI_DIR / "company_breakdown.csv", tables["company_breakdown"], ["company", "count", "percentage"])
    write_csv(POWERBI_DIR / "location_distribution.csv", tables["location_distribution"], ["location", "count", "percentage"])
    write_csv(POWERBI_DIR / "seniority_breakdown.csv", tables["seniority_breakdown"], ["seniority_level", "count", "percentage"])
    write_csv(POWERBI_DIR / "top_skills_requested.csv", tables["top_skills_requested"], ["skill", "count", "percentage"])
    write_csv(POWERBI_DIR / "top_tools_technologies.csv", tables["top_tools_technologies"], ["tool_technology", "count", "percentage"])
    write_csv(POWERBI_DIR / "job_skill_tool_bridge.csv", tables["job_skill_tool_bridge"], CSV_COLUMNS["job_skill_bridge"])
    write_csv(POWERBI_DIR / "job_location_bridge.csv", tables["job_location_bridge"], CSV_COLUMNS["location_bridge"])
    write_csv(POWERBI_DIR / "project_recommendations_powerbi.csv", recommendations, CSV_COLUMNS["recommendations"])

    manifest = {
        "source_dataset": str(INPUT_CSV.relative_to(PROJECT_ROOT)),
        "output_folder": str(POWERBI_DIR.relative_to(PROJECT_ROOT)),
        "tables": sorted(path.name for path in POWERBI_DIR.glob("*.csv")),
    }
    (POWERBI_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def print_summary(tables: dict[str, list[dict[str, object]]]) -> None:
    """Print a concise market analysis summary."""
    print("Power BI Market Analysis Pipeline")
    print("=" * 38)
    print(f"Source: {INPUT_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Jobs analyzed: {len(tables['jobs_powerbi'])}")
    print(f"Output folder: {POWERBI_DIR.relative_to(PROJECT_ROOT)}")

    print("\nTop skills requested:")
    for row in tables["top_skills_requested"][:8]:
        print(f"  - {row['skill']}: {row['count']}")

    print("\nTop tools/technologies:")
    for row in tables["top_tools_technologies"][:8]:
        print(f"  - {row['tool_technology']}: {row['count']}")

    print("\nTop categories:")
    for row in tables["role_category_breakdown"][:5]:
        print(f"  - {row['category']}: {row['count']}")


def analyze_market() -> None:
    """Run the full analysis pipeline."""
    ensure_output_dir()
    jobs = read_jobs()
    tables = build_powerbi_tables(jobs)
    recommendations = build_recommendations(tables)
    write_outputs(tables, recommendations)
    print_summary(tables)


def main() -> None:
    """Script entry point."""
    analyze_market()


if __name__ == "__main__":
    main()
