# 📚 AI Document Assistant

A professional, production-grade **Retrieval-Augmented Generation (RAG)** Document Intelligence Chatbot built with **Streamlit**, **LangChain**, **Google Gemini 2.5 Flash**, **HuggingFace Embeddings**, and **FAISS**.

---

## 🌟 Key Features

- **📄 Multi-Document Processing**: Supports simultaneous upload and processing of **PDF**, **DOCX**, and **TXT** files.
- **⚡ Advanced RAG Pipeline**: Uses `all-MiniLM-L6-v2` HuggingFace embeddings indexed in an in-memory **FAISS** vector store.
- **🎯 Strict Anti-Hallucination QA**: Powered by **Google Gemini 2.5 Flash** (`temperature=0.0`) strictly constrained to retrieved context.
- **🔍 Source Citations & Page Tracking**: Automatically extracts, cites, and displays exact document names, page numbers, and text snippets.
- **📈 Similarity Confidence Score**: Calculates cosine/distance similarity confidence percentage (High, Medium, Low) for every retrieved answer.
- **📑 Executive Document Summary**: Generates structured executive overviews, key findings, and core takeaways.
- **❓ Interactive Quiz Generator**: Generates custom multiple-choice quizzes based on uploaded document content with automated scoring and explanations.
- **🧠 Concept Flashcards**: Creates interactive study flashcards (Question/Answer flip view) for quick revision.
- **📊 Live Dashboard Statistics**: Real-time metrics tracking active documents, total text chunks, word count, and character counts.
- **⚙️ Configurable System Control**: Adjustable top-k retrieval slider, temperature tuning, and system status indicators.

---

## 📁 Project Architecture

```
AI-Document-Assistant/
│
├── app.py              # Main Streamlit web application & tab interface
├── rag_pipeline.py     # RAG chain, FAISS vector store, Gemini LLM & generators
├── utils.py            # File loaders (PDF, DOCX, TXT), text splitter & stats
├── styles.py           # Custom CSS styling system & glassmorphism cards
├── prompts.py          # Centralized prompt engineering for RAG, Summary, Quiz, Flashcards
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
└── README.md           # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites

- Python 3.9+ installed on your system.
- A **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/)).

### 2. Environment Setup

Clone or open the project folder:

```bash
cd "AI-Document-Assistant"
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### 5. Launch Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🖥️ User Interface Overview

The interface is organized into 5 dedicated tabs:

1. **💬 Chat Tab**: Ask natural language questions, view answers with confidence percentages, and expand source chunks to inspect page numbers and quotes.
2. **📄 Summary Tab**: Click to generate and export an executive summary of all uploaded documents.
3. **❓ Quiz Generator Tab**: Build an interactive multiple-choice test from your documents, submit choices, and view score breakdown.
4. **🧠 Flashcards Tab**: Flip through concept cards to test recall and study document terminology.
5. **⚙️ Settings Tab**: Inspect model parameters, set top-k retrieval depth, and verify environment health.

---

## 🛠️ Technology Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Orchestration**: [LangChain](https://www.langchain.com/)
- **LLM**: [Google Gemini 2.5 Flash](https://ai.google.dev/)
- **Embeddings**: [HuggingFace sentence-transformers (`all-MiniLM-L6-v2`)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Vector Database**: [FAISS (Facebook AI Similarity Search)](https://github.com/facebookresearch/faiss)
- **Document Loaders**: `PyPDFLoader`, `python-docx`, `TextLoader`
