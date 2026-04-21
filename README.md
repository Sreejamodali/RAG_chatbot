# 🧠 RAG Chatbot (Local) — Setup & Run Guide

This repository contains a Retrieval-Augmented Generation (RAG) chatbot that uses a vector store (Qdrant), LangChain for orchestration, and local model/embedding support (e.g., Ollama). The instructions below explain how to set up and run the project locally on Windows (PowerShell) and how to use the included Dockerfile when desired.

---

**Prerequisites**
- **Python:** `3.8` or newer installed and available on `PATH`.
- **pip:** Python package installer (usually included with Python).
- **Virtual environment tool:** `venv` (bundled with Python).
- **Git:** to clone the repository (optional if you already have the files).
- **Docker (optional):** if you prefer running via container.
- **Network access:** to install packages and (optionally) to pull model images if using remote model services.

---

**Quick Notes about this repo**
- The main entrypoints are `main.py` and `main1.py` — inspect them to decide which run mode you need.
- Utility modules: `chatbot_manager.py`, `database_manager.py`.
- Dependency list is in `requirements.txt`.

---

**1) Clone & open the project**
If you don't already have the repository locally, clone it and change directory:

```
git clone <repo-url>          # or use your local copy
cd c:\Users\SREEJA.M\Downloads\chatbot_LLMs\chatbot_LLMs\RAG
```

**2) Create a Python virtual environment (PowerShell)**
Run these commands in PowerShell (`pwsh.exe`):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents script execution, run (as admin) once to allow the activation script:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3) Install Python dependencies**
With the virtual environment active:

```
pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, check the error output for missing build tools (e.g., `wheel`, VC++ on Windows) and install them.

---

**4) Environment variables and configuration**
This project may use external API keys or environment settings depending on your configuration (for example, if you enable Ollama or remote model/embedding services). Common variables you may need to set:

- `OPENAI_API_KEY` — if you add OpenAI support.
- `DATABASE_URL` — if the project is configured with a database connection.
- `QDRANT_URL` / `QDRANT_API_KEY` — if using a remote Qdrant instance instead of local.

Set them in PowerShell like this:

```
$env:OPENAI_API_KEY = "your_api_key_here"
$env:DATABASE_URL = "sqlite:///./mydb.sqlite"
```

(Check your code for exact env var names — search for `os.getenv` or config constants.)

---

**5) Running the application (development)**
Choose the main script you want to run. Typical commands:

```
python main.py
# or
python main1.py
```

If the project exposes a web UI (e.g., Streamlit or FastAPI), the console output will show the URL (commonly `http://localhost:8501` or `http://127.0.0.1:8000`). Open that in your browser.


**6) Using Docker and Docker Compose (recommended for local/portable use)**

You can run the entire stack (Qdrant + app) with Docker Compose. This is the easiest way to get started on any system with Docker:

```
# 1. Copy .env.example to .env and fill in your values (if needed)
cp .env.example .env

# 2. Build and start all services
docker compose up --build

# 3. Stop services
docker compose down
```

This will start both Qdrant (vector DB) and the chatbot app. The app will be available at http://localhost:8501 (or the port you set in compose).

If you want to build/run the app container alone (without Compose):

```
docker build -t rag_chatbot:local .
docker run --rm -it -p 8501:8501 --env-file .env rag_chatbot:local
```

Adjust environment variables and ports to match the application's configuration.

---

**7) Common workflows**
- Rebuild dependencies after editing `requirements.txt`:

```
pip install -r requirements.txt
```

- Recreate virtual environment (if something breaks):

```
deactivate
Remove-Item -Recurse -Force ./.venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

**8) Troubleshooting**
- If a package fails to install, run the command shown in the error and search for the platform-specific solution (Windows often needs Visual C++ Build Tools).
- If the app cannot connect to Qdrant or other services, verify the `QDRANT_URL` and that the service is running and accessible.
- For permission issues activating venv on PowerShell, use `Set-ExecutionPolicy` shown above.

---

**9) Next steps / recommended improvements**
- Add a `.env.example` listing required environment variables.
- Add a `Makefile` or `psake` script for common tasks.
- Add a short `docker-compose.yml` to orchestrate Qdrant + app locally.

---

If you'd like, I can:
- run the project locally in this environment to verify it starts,
- add a `.env.example` file, or
- create a `docker-compose.yml` to run Qdrant + the app together.

---

File updated: `README.md`
# 🧠 RAG Chatbot with Qdrant, Ollama, and LangChain

This project is a Retrieval-Augmented Generation (RAG) chatbot built using Qdrant for vector storage, LangChain for orchestration, and Ollama for embedding and language model support. It enables document-based question answering from local files (PDF, CSV, Excel, etc.).

---

## 🚀 Features

- Load and chunk documents intelligently
- Store and retrieve documents using Qdrant
- Generate embeddings with Ollama (Llama 3, etc.)
- Streamlit interface for querying
- Fast, local, and customizable

---

## 📁 Folder Structure

