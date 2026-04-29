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

---

## 📂 Data Format

Example input (stored in S3):

```json
{
  "source_file": "incoming/production_data_2026-03-08.csv",
  "processed_at": "2026-04-28T11:02:04",
  "lines": [
    {
      "production_line": "Line_A",
      "average_cycle_time_seconds": 40.5,
      "completed_cycles": 2,
      "status": "stable"
    }
  ]
}

## n8n Workflow

The automation pipeline is implemented using n8n.

Workflow file:
n8n/workflow.json
