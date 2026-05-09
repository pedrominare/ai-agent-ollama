# Document Agent with Memory

A Python agent that ingests accounting documents, reports, and spreadsheets; answers questions in natural language; and keeps persistent memory (documents and conversation).

---

> **Quick guide:** For a concise walkthrough, see [GUIA_USO.md](GUIA_USO.md).

## Table of contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Step-by-step installation](#3-step-by-step-installation)
4. [Configuration](#4-configuration)
5. [Project architecture](#5-project-architecture)
6. [Files and responsibilities](#6-files-and-responsibilities)
7. [Step-by-step usage](#7-step-by-step-usage)
8. [Maintenance workflow](#8-maintenance-workflow)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

### What the agent does

1. **Ingests documents** ? PDF, Excel (.xlsx, .xls), Word (.docx)
2. **Stores in persistent memory** ? on-disk vector database (ChromaDB)
3. **Answers questions** ? retrieves relevant passages and generates an answer via an LLM
4. **Keeps conversation context** ? understands follow-ups like ?what about April??

### Key concepts

| Concept | Explanation |
|---------|-------------|
| **RAG** | Retrieval-Augmented Generation: retrieves passages from documents and uses them as context for the LLM |
| **Embeddings** | Numeric vectors representing text meaning (enables semantic search) |
| **Vector store** | Stores embeddings; finds passages ?similar? to the question |
| **LLM** | Language model (OpenAI or Ollama) that produces the final answer |

### Simplified flow

```
Documents ? Text extraction ? Chunks ? Embeddings ? ChromaDB (disk)
                                                        ?
Question ? Question embedding ? Similarity search ? Relevant passages
                                                        ?
         Passages + History + Question ? LLM ? Answer
```

---

## 2. Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **~2 GB disk** for embedding models (downloaded on first run)
- **One LLM option:**
  - **OpenAI**: OpenAI account + API key (paid)
  - **Ollama**: installed locally (free, runs on your machine)

---

## 3. Step-by-step installation

### Step 1: Open a terminal in the project folder

**Windows (PowerShell):**

```powershell
cd path\to\ai-agent-ollama\ai_src
```

**Linux / macOS:**

```bash
cd /path/to/ai-agent-ollama/ai_src
```

### Step 2: Create a virtual environment

The virtual environment isolates project dependencies.

**Windows:**

```powershell
python -m venv venv
```

**Linux / macOS:**

```bash
python3 -m venv venv
```

### Step 3: Activate the virtual environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

When active, the prompt should show `(venv)` at the beginning.

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

The first install may take a few minutes. `sentence-transformers` will download the embedding model (~400 MB) on first use.

### Step 5: Verify installation

```bash
python -c "import chromadb; import langchain; print('OK')"
```

If there is no error, the installation is correct.

---

## 4. Configuration

### `.env` file

1. Copy the example file:

   **Windows (CMD):** `copy .env.example .env`  
   **PowerShell:** `Copy-Item .env.example .env`  
   **Linux / macOS:** `cp .env.example .env`

2. Edit `.env` in a text editor.

**Option A ? OpenAI (cloud answers):**

```
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

**Option B ? Ollama (local, free):**

```
LLM_PROVIDER=ollama
```

For Ollama you should:

1. Install from https://ollama.com  
2. Keep the Ollama service running (app or `ollama serve`, depending on install)  
3. Pull a chat model. This project?s code defaults to **`mistral`**:

   ```bash
   ollama pull mistral
   ```

### Environment variables (GitHub Secrets and Variables)

All settings below can be set via **environment variables** (local `.env` or **GitHub Actions** under *Settings ? Secrets and variables ? Actions*).

| Variable | GitHub type | Description | Default |
|----------|-------------|-------------|---------|
| `OPENAI_API_KEY` | Secret | OpenAI API key | ? |
| `LLM_PROVIDER` | Variable | `openai` or `ollama` | `ollama` |
| `OLLAMA_BASE_URL` | Variable | Ollama base URL | `http://localhost:11434` |
| `VECTOR_DB_PATH` | Variable | Vector store directory | `data/chroma_db` |
| `CONVERSATION_FILE` | Variable | Conversation history file | `data/conversation.json` |
| `MAX_HISTORY_TURNS` | Variable | Question/answer turns to keep | `5` |
| `EMBEDDING_MODEL` | Variable | Embedding model id | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

**On GitHub:** use *Secrets* for sensitive values (e.g. `OPENAI_API_KEY`) and *Variables* for the rest.

---

## 5. Project architecture

### Run modes

The project has two implementations of the same RAG flow:

| Mode | Files | When to use |
|------|-------|-------------|
| **Manual** | `agent.py`, `vector_store.py`, `ingest.py` | Direct implementation without LangChain |
| **LangChain** | `agent_langchain.py`, `ingest_langchain.py` | Use the LangChain stack |

Add `--langchain` on the command line for LangChain mode. The default is manual mode.

### Data flow

```
main.py (CLI)
    |
    +-- ingest ? agent.ingestir_documento()
    |               |
    |               +-- ingest.extrair_texto()  ? extracted text
    |               +-- vector_store.dividir_texto()  ? chunks
    |               +-- vector_store.obter_embeddings()  ? vectors
    |               +-- ChromaDB.add()  ? persistence
    |
    +-- ask ? agent.responder_pergunta()
    |               |
    |               +-- ChromaDB.query()  ? relevant passages
    |               +-- memory.get_history_messages()  ? history
    |               +-- LLM (OpenAI/Ollama)  ? answer
    |               +-- memory.add_turn()  ? save to history
    |
    +-- clear ? memory.clear()  ? delete history
```

---

## 6. Files and responsibilities

### config.py

Central configuration: paths, `.env` keys, embedding model.

### main.py

Command-line interface. Handles `ingest`, `ask`, `clear` and flags `--replace`, `--langchain`.

### ingest.py

- `extrair_pdf()` ? PDF via pypdf  
- `extrair_excel()` ? Excel via openpyxl  
- `extrair_docx()` ? Word via python-docx  
- `extrair_texto()` ? picks extractor by file extension  

### vector_store.py

- `criar_cliente()` ? persistent ChromaDB  
- `obter_embeddings()` ? sentence-transformers  
- `dividir_texto()` ? chunking with overlap  
- `deletar_documento()` ? remove chunks by document name (for `--replace`)  

### agent.py (manual mode)

- `ingestir_documento()` ? extract, chunk, embed, save to Chroma  
- `responder_pergunta()` ? retrieve, build prompt, call LLM  

### agent_langchain.py (LangChain mode)

- Uses LangChain loaders, text splitter, Chroma, and LLM  
- Same ingest/answer idea with framework abstractions  

### ingest_langchain.py

- `carregar_documento()` ? returns a LangChain `Document`  
- PDF uses `PyPDFLoader`; Excel/Word use `ingest.extrair_texto()` wrapped as documents  

### GUIA_USO.md

Step-by-step guide for installation and daily use.

### memory.py

- `add_turn()` ? save question and answer  
- `get_history_messages()` ? return history for the prompt  
- `clear()` ? delete the history file  

### Generated data (`data/`)

| Path | Contents |
|------|----------|
| `chroma_db/` | Vector store (document embeddings) |
| `conversation.json` | Question/answer history |

---

## 7. Step-by-step usage

### 7.1 First run: ingest a document

**Windows:**

```powershell
python main.py ingest "..\DESPESAS_GESTAO_2025_RELATORIO_CIRCUNSTANCIADO.xlsx"
```

**Linux / macOS:**

```bash
python main.py ingest "../DESPESAS_GESTAO_2025_RELATORIO_CIRCUNSTANCIADO.xlsx"
```

**Expected output:** `Ingerido: DESPESAS_GESTAO_2025_RELATORIO_CIRCUNSTANCIADO.xlsx (N chunks)` (or the English equivalent if messages are localized).

On first run the embedding model downloads automatically (may take a while).

### 7.2 Ask a question

```bash
python main.py ask "What was the total expenses in May?"
```

The agent retrieves relevant passages and generates an answer.

### 7.3 Follow-up question (conversation memory)

```bash
python main.py ask "What was the total expenses in May?"
python main.py ask "What about April?"
```

The second question uses conversation history to interpret ?April?.

### 7.4 Add more documents (accumulate)

```bash
python main.py ingest "../BACKUP DO ESTATUTO SOCIAL.pdf"
python main.py ingest "../demonstrativo_fev_2025.xlsx"
```

Each document is added to the existing store.

### 7.5 Replace a document (maintenance)

```bash
python main.py ingest "../relatorio_gestao.xlsx" --replace
```

Removes the previous version of the same file and inserts the new one.

### 7.6 Clear conversation history

```bash
python main.py clear
```

**Note:** ingested documents stay in the vector store; only Q/A history is cleared.

### 7.7 LangChain mode

```bash
python main.py ingest "../arquivo.pdf" --langchain
python main.py ask "your question" --langchain
```

LangChain uses a separate collection (`documentos_langchain`), so vectors and history are not shared with manual mode.

---

## 8. Maintenance workflow

### Stable documents (one-time)

Ingest once and keep in the store:

```bash
python main.py ingest "../estatuto.pdf"
python main.py ingest "../regimento_interno.pdf"
```

### Recurring documents (monthly)

Use distinct filenames per month:

```bash
python main.py ingest "../demonstrativo_jan_2025.xlsx"
python main.py ingest "../demonstrativo_fev_2025.xlsx"
python main.py ingest "../demonstrativo_mar_2025.xlsx"
```

The agent keeps all months and can compare periods.

### Replacement (rare)

When you need to fix or refresh a document:

```bash
python main.py ingest "../relatorio_corrigido.xlsx" --replace
```

---

## 9. Troubleshooting

### ?Nenhum documento foi ingerido ainda? / no documents ingested

Run `ingest` before `ask`. Check the file path.

### PDF/Excel read errors

- PDF: file may be corrupt or protected.  
- Excel: ensure the file is not open in another program.

### ?Erro ao chamar Ollama? / Ollama errors

- Is Ollama installed and running?  
- Run `ollama pull mistral` (or the model name configured in code).

### `OPENAI_API_KEY` errors

- Ensure `.env` exists and contains `OPENAI_API_KEY=sk-...`  
- For Ollama, set `LLM_PROVIDER=ollama` and you can omit the key.

### Slow first run

The embedding model downloads the first time; later runs are faster.

### Conversation memory issues

- Check `data/conversation.json` exists and is valid JSON.  
- Run `python main.py clear` and try again.

---

## Command summary

| Command | Description |
|---------|-------------|
| `python main.py ingest <file>` | Add document to the store |
| `python main.py ingest <file> --replace` | Replace existing document |
| `python main.py ask "<question>"` | Ask the agent |
| `python main.py clear` | Clear conversation history |
| Add `--langchain` | Use LangChain implementation |
