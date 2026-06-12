# Saudi AI Career Intelligence

AI-powered labor market intelligence for Saudi AI, data, and technology careers in Saudi Arabia.

## Overview

Saudi AI Career Intelligence is a portfolio-focused AI/data analytics project that turns real Saudi job-market data and national strategy documents into actionable career guidance. The repository captures parsed job postings, market analysis outputs, and the foundation for a retrieval-augmented career assistant.

## Why This Matters

Saudi Arabia is investing heavily in AI, data, and digital transformation, but students and early-career professionals often lack visibility into which roles, skills, and projects align with real hiring demand.

This project helps bridge that gap with structured labor market intelligence, practical market signals, and early-stage career recommendation planning.

## Problem Statement

Saudi AI and data career search is fragmented:

- Job descriptions use inconsistent role titles across AI, data, and software tracks.
- Skills and tools are listed inconsistently, making resume positioning difficult.
- Strategy documents and national initiatives are hard to connect to actual hiring demand.

This project organizes those inputs into a more usable view for recruiting, portfolio planning, and early-career decision support.

## Data Sources

### Job Market Data

- 72 parsed LinkedIn job postings
- Role category breakdown
- Sector breakdown
- Skills/tools frequency analysis
- Power BI-ready CSV exports

### Strategy & Context Documents

- Vision 2030 reports
- AI governance documents
- Skills frameworks
- Personal profile

## System Architecture

![Architecture Diagram](docs/architecture.png)

## Current Project Status

| Component | Status |
|----------|--------|
| Job posting parsing | Complete |
| Market analysis pipeline | Complete |
| Power BI-ready exports | Complete |
| Dashboard design | In progress |
| RAG assistant skeleton | In progress |
| Streamlit prototype | In progress |
| Deployment | Planned |

## Features

- Structured parsing of Saudi AI job postings
- Role category and sector analysis
- Skills and tools frequency extraction
- Power BI-ready analytics exports
- RAG assistant architecture planning
- Documentation and portfolio-ready presentation

## Market Analysis Pipeline

The market analysis pipeline converts parsed job postings into dashboard-ready outputs, including role and sector summaries, skills and tools frequency, company signals, and seniority/location breakdowns.

## Power BI Dashboard Plan

The dashboard plan uses `data/market_analysis/powerbi` exports to visualize job-market signals with summary charts for:

- job and role distribution
- sector demand
- skills and tools
- company frequency
- location and seniority patterns

## RAG Assistant Plan

The RAG plan is based on a document retrieval track that indexes job postings, strategy reports, skills frameworks, and personal profile data. The system is designed to support career questions with chunking, embeddings, and Chroma-based retrieval.

## Results & Progress

- 72 parsed LinkedIn job postings
- Role category breakdown completed
- Sector distribution generated
- Skills/tools frequency analysis produced
- Power BI-ready exports assembled
- Streamlit/RAG prototype skeleton built

## Repository Structure

- `data/` — raw inputs, processed job postings, market analysis exports
- `docs/` — architecture diagram, project story, dashboard guide, roadmap, resume bullets
- `screenshots/` — placeholder visuals
- `scripts/` — parsing and analysis pipelines
- `src/` — prototype app, document ingestion, chunking, embeddings, retrieval
- `.env.example` — API key template
- `requirements.txt` — Python dependencies

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your OpenAI key:
   ```bash
   copy .env.example .env
   ```
3. Parse raw job postings:
   ```bash
   python scripts/parse_job_applications.py
   ```
4. Generate market outputs:
   ```bash
   python scripts/analyze_market.py
   ```
5. Run the Streamlit prototype:
   ```bash
   streamlit run src/app.py
   ```

## Roadmap

- Finalize Power BI dashboard visuals
- Build the RAG retrieval pipeline with Chroma embeddings
- Refine the Streamlit career intelligence prototype
- Add deployment packaging and delivery

## Portfolio Value

This project demonstrates practical AI/data product work with real labor market inputs, including:

- parsing and structuring job-market data
- analytics pipeline design
- dashboard-ready output generation
- retrieval-based career intelligence planning

## Screenshots

- `screenshots/dashboard-preview.png` — planned
- `screenshots/data-pipeline.png` — planned
- `screenshots/rag-assistant-preview.png` — planned

> Screenshot assets will be replaced as the dashboard and Streamlit prototype mature.
