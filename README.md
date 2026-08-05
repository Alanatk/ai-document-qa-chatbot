# 📚 AI Document Intelligence Chatbot

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-documentchatbot.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://www.langchain.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-orange.svg)](https://ai.google.dev/)
[![Vector Store](https://img.shields.io/badge/VectorStore-FAISS-blueviolet.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 **Live Application**: [https://ai-documentchatbot.streamlit.app/](https://ai-documentchatbot.streamlit.app/)

A production-grade **Retrieval-Augmented Generation (RAG)** Document Intelligence Chatbot built with **Streamlit**, **LangChain**, **Google Gemini 2.5 Flash**, **HuggingFace Embeddings**, and **FAISS**.

---

## 🌟 Key Features

- **📄 Multi-Document Processing**: Supports simultaneous upload and processing of **PDF**, **DOCX**, and **TXT** files.
- **⚡ Advanced RAG Pipeline**: Uses `all-MiniLM-L6-v2` HuggingFace embeddings indexed in an in-memory **FAISS** vector store.
- **🎯 Strict Anti-Hallucination QA**: Powered by **Google Gemini 2.5 Flash** (`temperature=0.0`) strictly constrained to retrieved context.
- **⏳ Resilient API Handling**: Includes automatic exponential backoff retry logic and seamless model fallback (`gemini-2.5-flash` ➡️ `gemini-1.5-flash`) for Gemini Free Tier rate limits.
- **🔍 Source Citations & Page Tracking**: Automatically extracts, cites, and displays exact document names, page numbers, match distance, and text snippets.
- **📈 Similarity Confidence Score**: Calculates normalized cosine/distance similarity confidence percentage (High, Medium, Low) for every retrieved answer.
- **🏷️ Auto Key Topic Extraction**: Automatically analyzes document chunks to generate clickable topic pills for quick exploration.
- **📑 Executive Document Summary**: Generates structured executive overviews, key findings, and downloadable Markdown/TXT summaries.
- **⚔️ Multi-Document Comparison**: Generates side-by-side comparative matrices across multiple uploaded documents.
- **❓ Interactive Quiz Generator**: Creates custom multiple-choice tests from document contents with automated scoring and instant feedback.
- **🧠 Concept Flashcards**: Interactive flashcards (Question/Answer flip view) for studying document terminology.
- **📊 Live Dashboard Statistics**: Real-time metrics tracking active documents, total text chunks, word count, character counts, and index build times.

---

## 📁 Project Architecture

```
ai-document-qa-chatbot/
│
├── app.py              # Main Streamlit web application & multi-tab interface
├── rag_pipeline.py     # RAG chain, FAISS vector store, Gemini LLM retry & fallback
├── utils.py            # Document parsers (PDF, DOCX, TXT), text splitter & statistics
├── styles.py           # Custom CSS styling system & glassmorphic UI components
├── prompts.py          # Centralized prompt engineering for RAG, Summary, Quiz & Flashcards
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Protected secrets & environment exclusions
└── README.md           # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites

- Python 3.9 or higher installed.
- A free **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/)).

### 2. Clone the Repository

```bash
git clone https://github.com/Alanatk/ai-document-qa-chatbot.git
cd ai-document-qa-chatbot
```

### 3. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### 6. Launch Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## ☁️ Free Deployment on Streamlit Cloud

1. Push your repository to GitHub:
   ```bash
   git remote add origin https://github.com/Alanatk/ai-document-qa-chatbot.git
   git push -u origin main
   ```
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** -> Select your repo `Alanatk/ai-document-qa-chatbot`, Branch `main`, Main file `app.py`.
4. Under **Advanced settings...** -> **Secrets**, paste your Gemini API key:
   ```toml
   GOOGLE_API_KEY = "your_actual_gemini_api_key_here"
   ```
5. Click **Deploy!**

---

## 🖥️ User Interface Overview

The app features 5 dedicated tabs:

1. **💬 Chat Tab**: Ask natural language questions, view answers with confidence percentages, click key topic badges, and inspect page numbers and source quotes.
2. **📄 Summary Tab**: Generate executive document overviews and multi-document comparative matrices with MD/TXT download options.
3. **❓ Quiz Generator Tab**: Build interactive multiple-choice tests from your documents, submit answers, and view score breakdown.
4. **🧠 Flashcards Tab**: Flip through concept cards to test recall and study document terms.
5. **⚙️ Settings Tab**: Inspect model parameters, top-k retrieval depth, and verify system status.

---

## 🛠️ Technology Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Orchestration**: [LangChain](https://www.langchain.com/)
- **LLM**: [Google Gemini 2.5 Flash](https://ai.google.dev/)
- **Embeddings**: [HuggingFace sentence-transformers (`all-MiniLM-L6-v2`)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss)
- **Document Parsers**: `PyPDFLoader`, `python-docx`, `TextLoader`

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
