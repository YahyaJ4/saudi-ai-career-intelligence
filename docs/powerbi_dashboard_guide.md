# Power BI Dashboard Guide

## Dashboard name

Saudi AI Career Intelligence Market Dashboard

## Goal

Create a polished, recruiter-ready dashboard that surfaces Saudi AI/data job market signals from the parsed dataset. The dashboard is designed to help students, recruiters, and hiring managers understand role demand, sector patterns, and portfolio gaps.

## Data source

Import data from:

```text
data/market_analysis/powerbi/
```

Key files:

- `jobs_powerbi.csv`
- `role_category_breakdown.csv`
- `sector_breakdown.csv`
- `top_skills_requested.csv`
- `top_tools_technologies.csv`
- `company_breakdown.csv`
- `location_distribution.csv`
- `seniority_breakdown.csv`
- `job_skill_tool_bridge.csv`
- `job_location_bridge.csv`
- `project_recommendations_powerbi.csv`

## Data model

Use `jobs_powerbi.csv` as the central fact table. Connect bridge tables by `job_number` for skill/tool and location detail.

Relationships:

- `jobs_powerbi[job_number]` → `job_skill_tool_bridge[job_number]`
- `jobs_powerbi[job_number]` → `job_location_bridge[job_number]`

Use the frequency tables as supporting summary datasets for clean visuals.

## Page 1 — Market overview

Purpose: Help viewers absorb the dataset at a glance.

Recommended visuals:

- Total jobs card
- Role category breakdown bar chart
- Sector distribution donut chart
- Company frequency table
- Data quality callout for location / seniority coverage

Message:

> This dataset currently covers 72 Saudi AI/data job postings, with strong signals in Data Science, AI Engineering, Consulting, GenAI/LLM, and Software Engineering.

## Page 2 — Skills and tools demand

Purpose: Show the capabilities employers ask for most often.

Recommended visuals:

- Top skills bar chart
- Top tools/technologies bar chart
- Role category × skill/tool matrix
- Sector filter

Insights:

- AI and Machine Learning are the strongest skill signals.
- Deployment and cloud tooling are visible gaps worth highlighting.
- Key technology signals include PyTorch, TensorFlow, Docker, SQL, Azure, AWS, LangChain, and MLOps.

## Page 3 — Roles, sectors, and companies

Purpose: Show where demand lives in the Saudi market.

Recommended visuals:

- Role category breakdown
- Sector breakdown
- Top company frequency
- Role category by sector stacked bar

Interpretation:

> The current dataset is weighted toward technology roles, with fintech and consulting appearing as valuable adjacent opportunities.

## Page 4 — Location and seniority

Purpose: Clarify geographic and experience signals.

Recommended visuals:

- Location distribution chart
- Seniority breakdown chart
- Table for jobs missing explicit location
- Experience-level slicer

Insight:

> Many postings lack explicit location metadata. Where location is specified, Saudi Arabia and Riyadh are strong signals.

## Page 5 — Project recommendations

Purpose: Turn market analysis into practical portfolio actions.

Recommended visuals:

- Project recommendation table
- Skill/tool coverage matrix for proposed projects
- Project priority card

Recommended sequence:

1. Saudi AI Job Market Dashboard
2. Fintech RAG Analyst
3. ML Prediction API with Docker

## Design guidance

- Keep visuals clean and professional.
- Use neutral backgrounds with dark accent colors.
- Prefer bar charts for rankings and breakdowns.
- Use slicers for role category, sector, and seniority.
- Keep narrative labels concise and actionable.

## Refresh workflow

1. Add new job postings to `data/job_postings/raw_text` or source PDFs.
2. Run:

```bash
python scripts/parse_job_applications.py
```

3. Run:

```bash
python scripts/analyze_market.py
```

4. Refresh Power BI.

