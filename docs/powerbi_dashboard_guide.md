# Power BI Dashboard Guide

## Dashboard Name

Saudi AI Career Intelligence - Market Dashboard

## Goal

Help Saudi CS/AI students and fresh graduates understand what the Saudi AI/data job market is asking for, which sectors and roles are most visible, and which projects can close the gap between student profiles and market demand.

## Data Source

Load CSV files from:

```text
data/market_analysis/powerbi/
```

Recommended files to import:

- `jobs_powerbi.csv`
- `top_skills_requested.csv`
- `top_tools_technologies.csv`
- `role_category_breakdown.csv`
- `sector_breakdown.csv`
- `company_breakdown.csv`
- `location_distribution.csv`
- `seniority_breakdown.csv`
- `job_skill_tool_bridge.csv`
- `job_location_bridge.csv`
- `project_recommendations_powerbi.csv`

## Suggested Data Model

Use `jobs_powerbi.csv` as the central fact table.

Relationships:

- `jobs_powerbi[job_number]` to `job_skill_tool_bridge[job_number]`
- `jobs_powerbi[job_number]` to `job_location_bridge[job_number]`

The frequency tables can be used as standalone summary tables for simple visuals.

## Page 1 - Market Overview

Purpose: Give a fast understanding of the 72-posting dataset.

Recommended visuals:

- Card: total jobs analyzed
- Card: number of role categories
- Card: number of sectors
- Bar chart: role category breakdown
- Donut chart: sector breakdown
- Table: top companies

Suggested message:

> The current dataset is heavily concentrated in technology roles, with visible demand across Data Science, AI Engineering, Consulting, GenAI / LLM, and Software Engineering.

## Page 2 - Skills And Tools Demand

Purpose: Show what the market repeatedly asks for.

Recommended visuals:

- Bar chart: top skills requested
- Bar chart: top tools/technologies
- Matrix: skill/tool by role category using `job_skill_tool_bridge`
- Slicer: role category
- Slicer: sector

Important signals from the first dataset:

- AI and Machine Learning dominate the skills side.
- PyTorch, TensorFlow, Docker, SQL, Azure, AWS, MLOps, RAG, and Kubernetes are strong tool/technology signals.
- Docker, SQL, Power BI, LangChain, and deployment are good portfolio gap areas.

## Page 3 - Roles, Sectors, And Companies

Purpose: Help students understand where demand appears.

Recommended visuals:

- Bar chart: role category breakdown
- Bar chart: sector breakdown
- Table: company breakdown
- Stacked bar: role category by sector

Suggested interpretation:

> For this student's target market, technology is the dominant sector, with fintech and consulting as smaller but strategically valuable focus areas.

## Page 4 - Location And Seniority

Purpose: Clarify where roles are based and how accessible they are for fresh graduates.

Recommended visuals:

- Bar chart: location distribution
- Bar chart: seniority breakdown
- Table: jobs with `Not specified` location
- Slicer: seniority level

Suggested interpretation:

> Many postings do not specify location clearly, but Saudi Arabia and Riyadh are visible. Seniority is mixed, so fresh graduates need projects that reduce perceived experience risk.

## Page 5 - Project Recommendations

Purpose: Translate market demand into portfolio actions.

Recommended visuals:

- Table: project recommendations
- Matrix: project vs skills/tools to show
- Card: highest priority project

Recommended project sequence:

1. Saudi AI Job Market Dashboard
2. Fintech RAG Analyst
3. ML Prediction API with Docker

Suggested interpretation:

> The portfolio should prove market awareness, AI engineering ability, and deployment readiness. The strongest immediate project is the dashboard itself, followed by a RAG app and Dockerized ML API.

## Dashboard Design Style

Use a clean professional style:

- background: white or very light gray
- accent color: deep green or blue
- charts: horizontal bars for rankings
- avoid decorative visuals
- keep page titles direct and readable
- use slicers for category, sector, and seniority

## Suggested Measures

Create these simple DAX measures:

```DAX
Total Jobs = COUNTROWS(jobs_powerbi)

Jobs With Location =
CALCULATE(COUNTROWS(jobs_powerbi), jobs_powerbi[has_location] = TRUE())

Jobs With Salary =
CALCULATE(COUNTROWS(jobs_powerbi), jobs_powerbi[has_salary] = TRUE())

Average Skills Per Job =
AVERAGE(jobs_powerbi[skills_tools_count])
```

## Refresh Workflow

1. Add new job postings PDF.
2. Run:

```bash
python scripts/parse_job_applications.py
```

3. Run:

```bash
python scripts/analyze_market.py
```

4. Refresh Power BI.

