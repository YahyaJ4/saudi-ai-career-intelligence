# Project Story

## Short Version

Saudi AI Career Intelligence is a retrieval-augmented career intelligence system that helps Saudi CS/AI students and fresh graduates understand the Saudi job market, identify required skills, and decide what projects, activities, and experiences to build before graduation.

## Personal Motivation

As a master's student entering the Saudi AI job market, I found it difficult to understand which skills, projects, and experiences employers actually valued. Job postings often mention many tools and responsibilities, but it is hard for students to know which signals matter most and how to prepare before graduation.

To solve this, I started collecting job postings I had applied to and used them as a real dataset. I built a pipeline that parses numbered LinkedIn job application PDFs, extracts job descriptions and requirements, and analyzes the roles, sectors, skills, tools, and experience levels appearing across the postings.

## What The Project Does

The system analyzes:

- job postings
- required skills and tools
- role categories
- sector demand
- company information
- career pathways
- personal profile data
- national AI and strategy documents

The long-term goal is to connect this data through a retrieval-augmented system so students can ask questions such as:

- What skills do AI Engineer roles in Saudi Arabia ask for most often?
- What projects should I build before graduation?
- How do Data Scientist and AI Engineer roles differ?
- Which sectors are hiring for GenAI and RAG skills?
- What is missing from my profile compared with the market?

## Why It Matters

Many students graduate with technical knowledge but without a clear map of what the market rewards. This project turns job-search uncertainty into structured career intelligence.

For students, it provides a practical way to prepare. For recruiters and employers, it demonstrates the ability to build useful AI systems around messy real-world data.

## Current Status

The first version uses 72 parsed job postings from a personal LinkedIn application-history dataset. It already generates market summaries for role categories, sectors, skills/tools, companies, and experience requirements.

The next version will add:

- LangChain retrieval
- Chroma vector storage
- Streamlit demo interface
- Dockerized setup
- student-facing career recommendations

## One-Sentence Pitch

I built a retrieval-augmented career intelligence system that analyzes Saudi AI/data job postings and career documents to help students understand market demand and prepare stronger projects before graduation.

