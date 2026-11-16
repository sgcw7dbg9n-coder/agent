\# Reconciliation Agent



An open-source AI agent that compares two datasets, finds where they disagree, and explains the discrepancies in plain language with recommended next actions.



\## Why I built this



Data reconciliation is one of those unglamorous but costly problems that shows up everywhere: finance teams checking a sales system against a ledger, operations comparing a point-of-sale export against warehouse records, anyone who has to confirm that two sources that are supposed to match actually do. It is usually done by hand or with brittle spreadsheets.



I wanted to solve a real problem while learning how to build an actual AI agent from the ground up, using only open-source tooling so there is no vendor lock-in and it can run for free. This project is the result: a working agent I understand end to end, not a black box.



\## What it does



Point it at two CSV files that share a key column (an order ID, transaction ID, SKU) and it will:



\- Find records that exist in one file but not the other

\- Detect duplicate records

\- Flag field-level mismatches (different quantities, prices, totals for the same record)

\- Produce a clear report grouped by issue type, with likely severity and recommended fixes



\## How it works



The design keeps the model doing what it is good at and the code doing what it is good at:



\- \*\*Deterministic engine (pandas):\*\* all the exact matching and comparison happens in Python. The language model never does arithmetic, so the numbers are always trustworthy.

\- \*\*Reasoning layer (LLM):\*\* the model takes the computed findings and turns them into a readable report. It is explicitly instructed never to invent or recompute numbers.

\- \*\*Agent loop:\*\* the agent is given tools (list datasets, reconcile datasets) and a goal, then decides for itself which tools to call and in what order.

\- \*\*Provider-agnostic:\*\* it talks to any OpenAI-compatible endpoint, so you can run it on a free hosted model (Groq), a cheap one (DeepSeek), or fully offline with a local model (Ollama), by changing one line in a config file.

\- \*\*Web UI (Streamlit):\*\* upload two files, pick the key and columns to compare, and get the report in the browser.



\## Tech stack



Python, pandas, the OpenAI-compatible client, Streamlit, and an open-weights LLM served through Groq.



\## Project structure
agent/

├── app.py Streamlit web interface

├── requirements.txt

├── data/ Sample datasets

├── recon/ Core package

│ ├── reconcile.py Deterministic comparison engine

│ ├── report.py LLM report generation

│ ├── agent.py Tool-calling agent loop

│ └── llm.py Provider-agnostic model client

└── scripts/ Helper scripts (data generation, connection tests)



\## Setup



```bash

conda create -n recon-agent python=3.11 -y

conda activate recon-agent

conda install -c conda-forge openai python-dotenv pandas streamlit -y

```



Create a `.env` file with your provider and key:
PROVIDER=groq

GROQ\_API\_KEY=your\_key\_here

GROQ\_MODEL=openai/gpt-oss-120b


Run the app:



```bash

streamlit run app.py

```



With no files uploaded it runs on the built-in sample data, so you can try it immediately.


