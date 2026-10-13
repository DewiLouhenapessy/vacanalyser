# VacAnalyser

VacAnalyser is a command-line tool that compares a job vacancy with a CV. It uses Mistral models to extract requirements from the vacancy, retrieve relevant CV passages, and produce an evidence-based match analysis.

## How it works

1. **Analyse the vacancy** — extract the job title, hard requirements, nice-to-haves, and keywords into structured data.
2. **Retrieve CV evidence** — split the CV into overlapping chunks, create embeddings, and find the passages most relevant to each hard requirement.
3. **Assess the match** — ask the model to evaluate each requirement using the retrieved CV passages as its source, and return strengths, improvement points, and a match estimate.

The match score is an AI-generated estimate, not a calculated or validated hiring metric. Review the cited evidence and use the result as decision support, not as an automated hiring decision.

## Requirements

- Python 3.10 or later
- A Mistral API key
- An internet connection for Mistral API calls

## Quick start

From the project directory, create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add your API key:

```dotenv
MISTRAL_API_KEY=your-mistral-api-key
```

Keep the key private. The `.env` file is excluded from Git.

## Run the matcher

Pass a plain-text vacancy file to the matcher:

```bash
python -m app.matcher data/vacature_example.txt
```

If no file is provided, the matcher analyses a built-in example vacancy:

```bash
python -m app.matcher
```

If `data/cv_store.json` does not exist, the app builds it on the first run. It uses the local `data/cv.txt` when present and otherwise falls back to the included `data/cv_example.txt`. The store is generated locally and is excluded from Git.

To rebuild the index after changing the CV, run:

```bash
python -c "from pathlib import Path; from app.rag import bouw_cv_store, maak_chunks; source = Path('data/cv.txt'); source = source if source.exists() else Path('data/cv_example.txt'); bouw_cv_store(maak_chunks(source.read_text(encoding='utf-8')))"
```

## Other commands

Analyse a vacancy and print its structured fields:

```bash
python -m app.analyser
```

Search the CV index. An optional argument replaces the default search query (`ervaring met Docker`):

```bash
python -m app.rag "ervaring met Docker"
```

## Tests

The analyser test makes a live Mistral API request, so configure `MISTRAL_API_KEY` before running it. Install `pytest` if it is not already available in your environment:

```bash
python -m pip install pytest
python -m pytest
```

## Project layout

```text
app/
  analyser.py   Extract structured vacancy information
  matcher.py    Retrieve CV evidence and assess the match
  rag.py        Chunk, embed, store, and search CV content
data/
  cv_example.txt      Example CV (used when no local CV is present)
  cv.txt              Optional local CV; excluded from Git
  cv_store.json       Generated CV chunks and embeddings; excluded from Git
  vacancy_example.txt Example vacancy
tests/
  test_analyser.py
```

## Privacy and API usage

The CV contains personal information. CV text is sent to Mistral to create embeddings, and vacancy text and retrieved CV passages are sent to Mistral for analysis. Only use data you are authorized to process, and review Mistral's data-handling terms before using real candidate information. API usage may incur charges.
