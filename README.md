# daily-production-analytics-siyao-2026 (n8n + AWS + OpenAI)

## 🚀 Overview

This project implements a lightweight data pipeline for analyzing production data using **n8n**, **AWS S3**, and **OpenAI**.

The system automatically:
- Loads production data from S3
- Parses and processes the data
- Generates structured insights using an LLM (GPT-4o-mini)

The goal is to simulate a **real-world factory analytics workflow** that detects performance trends and highlights potential issues.

## 🧠 Architecture
S3 (JSON data)
↓
Download (n8n)
↓
Parse JSON (Code node)
↓
Generate Prompt (Code node)
↓
OpenAI (GPT-4o-mini)
↓
Post-process Output


---

## 📦 Tech Stack

- **n8n** – workflow automation
- **AWS S3** – data storage
- **JavaScript** – data processing inside n8n
- **OpenAI API (GPT-4o-mini)** – AI-based analysis
