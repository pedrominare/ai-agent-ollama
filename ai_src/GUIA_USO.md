# Usage Guide ? Step by Step

Practical guide to install, configure, and use the document agent.

---

## Part 1: Installation (one-time)

### Step 1.1 ? Open a terminal in the project folder

**Windows (PowerShell):**

```powershell
cd path\to\ai-agent-ollama\ai_src
```

**Linux / macOS:**

```bash
cd /path/to/ai-agent-ollama/ai_src
```

### Step 1.2 ? Create and activate the virtual environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

The prompt should show `(venv)` at the start.

### Step 1.3 ? Install dependencies

```bash
pip install -r requirements.txt
```

Wait until it finishes (may take a few minutes).

### Step 1.4 ? Configure the LLM

**Option A ? OpenAI (paid, cloud):**

1. Copy the example env file:  
   **Windows:** `copy .env.example .env` or `Copy-Item .env.example .env`  
   **Linux / macOS:** `cp .env.example .env`
2. Edit `.env` and add your key:

   ```
   OPENAI_API_KEY=sk-your-key-here
   LLM_PROVIDER=openai
   ```

**Option B ? Ollama (free, local):**

1. Install Ollama: https://ollama.com  
2. Keep the Ollama service running  
3. In a terminal:

   ```bash
   ollama pull mistral
   ```

   (`mistral` matches the default in this project?s code.)

4. Create `.env` with:

   ```
   LLM_PROVIDER=ollama
   ```

---

## Part 2: Daily use

### Step 2.1 ? Activate the environment (if needed)

**Windows:**

```powershell
cd path\to\ai-agent-ollama\ai_src
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
cd /path/to/ai-agent-ollama/ai_src
source venv/bin/activate
```

### Step 2.2 ? Ingest a document

Put the file (PDF, Excel, or Word) somewhere accessible and run:

**Windows:**

```powershell
python main.py ingest "path\to\your\file.pdf"
```

**Linux / macOS:**

```bash
python main.py ingest "/path/to/your/file.pdf"
```

**Example with file in the parent folder:**

```bash
python main.py ingest "../DESPESAS_GESTAO_2025_RELATORIO_CIRCUNSTANCIADO.xlsx"
```

**Expected output:** `Ingerido: FILENAME.xlsx (N chunks)` (wording may match your CLI locale).

> On first use the embedding model downloads automatically (~400 MB).

### Step 2.3 ? Ask a question

```bash
python main.py ask "What was the total expenses in May?"
```

The agent answers based on ingested documents.

### Step 2.4 ? Continue the conversation

The agent remembers earlier turns:

```bash
python main.py ask "What was the total expenses in May?"
python main.py ask "What about April?"
```

The second question uses context from the first.

### Step 2.5 ? Add more documents

Each `ingest` appends to the store:

```bash
python main.py ingest "../estatuto.pdf"
python main.py ingest "../demonstrativo_fev_2025.xlsx"
```

### Step 2.6 ? Replace a document (when needed)

Use `--replace` to swap an old version for a new one:

```bash
python main.py ingest "../relatorio_atualizado.xlsx" --replace
```

### Step 2.7 ? Clear conversation history

Start a fresh conversation (documents stay in the store):

```bash
python main.py clear
```

---

## Part 3: Command summary

| Task | Command |
|------|---------|
| Add document | `python main.py ingest "path/to/file.pdf"` |
| Replace document | `python main.py ingest "path/to/file.pdf" --replace` |
| Ask a question | `python main.py ask "your question here"` |
| Clear history | `python main.py clear` |
| Use LangChain | Add `--langchain` to the command |

---

## Part 4: Suggested workflow

### Stable documents (one-time)

```bash
python main.py ingest "../estatuto.pdf"
python main.py ingest "../regimento_interno.pdf"
```

### Monthly documents (each month)

```bash
python main.py ingest "../demonstrativo_jan_2025.xlsx"
python main.py ingest "../demonstrativo_fev_2025.xlsx"
python main.py ingest "../demonstrativo_mar_2025.xlsx"
```

Use different names per month so data accumulates.

### Queries

```bash
python main.py ask "What were total expenses in January?"
python main.py ask "Compare January and February"
```

---

## Common issues

| Issue | Fix |
|-------|-----|
| No documents ingested | Run `ingest` before `ask` |
| File read error | Check path and that the file is not open elsewhere |
| Ollama error | Ensure Ollama is running; run `ollama pull mistral` |
| OpenAI error | Check `.env` has a valid `OPENAI_API_KEY` |
| Slow first run | Normal: embedding model is downloading |
