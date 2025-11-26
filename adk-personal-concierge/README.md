## Overview
Concierge Agent demo built with the Agent Development Kit (ADK). It pairs a FAISS vector store with `all-MiniLM-L6-v2` embeddings to retrieve watch data and images. Swap FAISS for any Google Cloud Vector Search backend and the embedding model for `gemini-embedding-001` as your needs grow.

## Prerequisites
- Python 3.9+ recommended
- Dependencies from `requirements.txt`
- ADK CLI installed and authenticated (Google API key in `.env`)

## Setup
1) Clone the repo and `cd` into `adk-personal-concierge`.
2) Install deps: `pip install -r requirements.txt`.
3) Create a `.env` in the repo root with `GOOGLE_API_KEY=...` (or your ADK-required key name).
4) Serve static assets: `python -m http.server --directory data/watches 9000` (defaults to `http://127.0.0.1:9000`).
5) Start ADK web: `adk web`.
6) Open the ADK UI (typically `http://127.0.0.1:8000`), select the `src` agent, and start a session.

## Notes
- Image base URL defaults to `http://127.0.0.1:9000`; override via `HAPPTIQ_IMAGE_BASE_URL` if hosting elsewhere.
- The demo ships with sample FAISS index and product metadata in `data/`; regenerate or replace as needed for your content.
- Any kind of feedback is much appreciated. Enjoy!
