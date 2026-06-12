# Saudi AI Career Intelligence - Project Progress

## Project Goal

Build a retrieval-augmented career intelligence system for Saudi CS/AI students and fresh graduates. The system helps students understand the Saudi job market, identify required skills, and decide what projects, activities, and experiences to build before graduation.

## Motivation

As a master's student entering the Saudi job market, it can be difficult to understand which skills, projects, and experiences actually matter. This project turns job postings, company information, national AI documents, and personal career data into a practical decision-support system.

## Target User

- Saudi CS/AI students
- Saudi fresh graduates
- Students preparing for AI engineering, data science, data engineering, fintech, consulting, and software roles

## Current Dataset

- 72 parsed LinkedIn job postings
- Source PDF: `data/raw_docs/linkedin_job_applications_numbered.pdf`
- Parsed CSV: `data/job_postings/processed/job_postings.csv`
- Parsed JSON: `data/job_postings/processed/job_postings.json`
- Raw posting text: `data/job_postings/raw_text/`
- Personal profile: `data/personal_profile/personal_profile_master.yaml`

## Built So Far

- Cleaned project folder structure.
- Created numbered PDF parser with `pypdf` and regex.
- Extracted 72 job postings.
- Validated missing and duplicate job numbers.
- Generated clean `job_postings.csv` and `job_postings.json`.
- Created `personal_profile_master.yaml`.
- Created initial market analysis files:
  - `data/market_analysis/role_category_breakdown.csv`
  - `data/market_analysis/sector_breakdown.csv`
  - `data/market_analysis/skills_tools_frequency.csv`
  - `data/market_analysis/company_frequency.csv`
  - `data/market_analysis/experience_breakdown.csv`
  - `data/market_analysis/market_summary.yaml`
  - `data/market_analysis/project_recommendations.yaml`
- Added Power BI-ready market analysis pipeline:
  - `scripts/analyze_market.py`
  - `data/market_analysis/powerbi/jobs_powerbi.csv`
  - `data/market_analysis/powerbi/top_skills_requested.csv`
  - `data/market_analysis/powerbi/top_tools_technologies.csv`
  - `data/market_analysis/powerbi/role_category_breakdown.csv`
  - `data/market_analysis/powerbi/sector_breakdown.csv`
  - `data/market_analysis/powerbi/company_breakdown.csv`
  - `data/market_analysis/powerbi/location_distribution.csv`
  - `data/market_analysis/powerbi/seniority_breakdown.csv`
  - `data/market_analysis/powerbi/project_recommendations_powerbi.csv`

## Initial Market Signals

- Most common role categories:
  - Data Science: 19
  - AI Engineering: 11
  - Consulting: 10
  - GenAI / LLM: 9
  - Software Engineering: 8
- Most common sectors:
  - Technology: 60
  - Fintech: 5
  - Consulting: 4
- Frequent skills/tools:
  - AI
  - Machine Learning
  - PyTorch
  - TensorFlow
  - Docker
  - SQL
  - Azure
  - AWS
  - MLOps
  - RAG
  - LLMs
  - Power BI

## Current Positioning

The project positions Yahya as an AI/Data engineer who can build practical AI systems using Python, PyTorch, RAG, data pipelines, and market analysis. The next step is to add stronger evidence for LangChain, Docker, Power BI, SQL, and deployment.

## Next Milestones

1. Build the Power BI dashboard from the generated CSV files.
2. Add screenshots or exported dashboard pages to the project README.
3. Build the LangChain + Chroma career RAG prototype.
4. Add Streamlit interface.
5. Dockerize the app.
6. Write polished GitHub README.
7. Prepare LinkedIn demo post and resume bullets.

## App Stack

- LangChain
- Chroma
- Streamlit
- Docker
- Python
- `pypdf`
- CSV/JSON/YAML data layer
