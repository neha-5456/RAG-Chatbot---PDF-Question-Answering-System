# 📄 RAG Chatbot — PDF Question Answering System

A production-ready Retrieval-Augmented Generation (RAG) chatbot that lets you upload PDFs and ask questions about their content. Built with LangChain, ChromaDB, and OpenAI.

---

## 🎯 What It Does

Upload any PDF → ask questions in natural language → get accurate answers grounded in your documents with source citations.

**Example:**
```
📄 Uploaded: company_policy.pdf
🧑 Q: "What is the leave policy for new employees?"
🤖 A: "New employees are entitled to 15 days of paid leave per year,
       accruing at 1.25 days per month..."
📚 Source: Page 12, Chunk 3
```

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  PDF Upload  │────▶│  Text Extraction │────▶│   Chunking   │
│  (PyPDF)     │     │  (page by page)  │     │  (500 chars) │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Answer     │◀────│   LLM (GPT-3.5) │◀────│  ChromaDB    │
│  + Sources   │     │ Context + Query  │     │  (Vectors)   │
└──────────────┘     └──────────────────┘     └──────┬───────┘
                                                      ▲
                                                      │
                                              ┌───────┴──────┐
                                              │  User Query  │
                                              │  (Embedding) │
                                              └──────────────┘
```

**RAG Pipeline Steps:**
1. **Load** — PDF pages extracted via PyPDFLoader
2. **Chunk** — Text split into 500-char overlapping chunks using RecursiveCharacterTextSplitter
3. **Embed** — Each chunk converted to vector embedding (OpenAI text-embedding-ada-002)
4. **Store** — Vectors indexed in ChromaDB for fast similarity search
5. **Retrieve** — User query embedded → top-4 similar chunks found via cosine similarity
6. **Generate** — Retrieved chunks + query + chat history sent to GPT-3.5-turbo → answer generated

---

## 🛠️ Tech Stack

| Component       | Technology              | Why                                  |
|-----------------|-------------------------|--------------------------------------|
| Framework       | LangChain               | Modular RAG pipeline orchestration   |
| Vector Store    | ChromaDB                | Lightweight, no setup needed         |
| LLM             | OpenAI GPT-3.5-turbo    | Fast, cost-effective generation      |
| Embeddings      | OpenAI Ada-002          | High-quality text embeddings         |
| PDF Parsing     | PyPDF                   | Reliable PDF text extraction         |
| UI              | Streamlit               | Rapid prototyping, built-in chat UI  |
| Memory          | ConversationBufferWindow| Maintains last 5 turns for follow-ups|

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-agents-portfolio.git
cd ai-agents-portfolio/01-rag-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 5. Run the app
```bash
streamlit run app.py
```

### 6. Test without UI (optional)
```bash
# Put a sample PDF in data/ folder first
python rag_engine.py
```

---

## 📁 Project Structure

```
01-rag-chatbot/
├── rag_engine.py       # Core RAG pipeline (load, chunk, embed, retrieve, generate)
├── app.py              # Streamlit chat interface
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
├── data/               # Sample PDFs (for testing)
├── screenshots/        # Demo screenshots
└── README.md
```

---

## ✨ Key Features

- **Multi-PDF Support** — Upload and query across multiple documents simultaneously
- **Source Citations** — Every answer shows which chunks and pages were used
- **Chat Memory** — Remembers last 5 conversations for follow-up questions
- **Chunk Overlap** — 50-char overlap prevents context loss at chunk boundaries
- **Similarity Search** — Top-4 most relevant chunks retrieved per query

---

## 🔧 Configuration

You can tune these parameters in `rag_engine.py`:

| Parameter        | Default | What it controls                          |
|------------------|---------|-------------------------------------------|
| `chunk_size`     | 500     | Characters per chunk (smaller = precise)  |
| `chunk_overlap`  | 50      | Overlap between chunks (prevents cutoffs) |
| `k` (retriever)  | 4       | Number of chunks retrieved per query      |
| `k` (memory)     | 5       | Number of past conversations remembered   |
| `temperature`    | 0       | LLM randomness (0 = deterministic)        |

---

## 🔮 Future Improvements

- [ ] Add support for DOCX, TXT, and web URLs
- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add re-ranking with cross-encoder for better retrieval
- [ ] Deploy on Hugging Face Spaces / Streamlit Cloud
- [ ] Add evaluation metrics (retrieval accuracy, answer faithfulness)
- [ ] Upgrade to Agentic RAG with LangGraph (see `02-agentic-rag/`)

---

## 📝 What I Learned

- How **text embeddings** capture semantic meaning and enable similarity search
- The importance of **chunk size and overlap** in retrieval quality
- How **ConversationalRetrievalChain** maintains context across multi-turn conversations
- Trade-offs between **retrieval precision vs recall** when tuning `k` parameter
- Why **source attribution** matters for trustworthy AI applications

---

## 📄 License

MIT
