"""
RAG Pipeline module for AI Document Assistant.
Handles HuggingFace embeddings generation, FAISS vector store indexing,
Google Gemini LLM integration with automatic rate-limit retry & fallback,
source citation tracking, confidence scoring, metadata filtering, summaries,
comparison, key topic extraction, and quiz/flashcard generators.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from prompts import (
    get_comparison_prompt,
    get_flashcard_prompt,
    get_key_topics_prompt,
    get_quiz_prompt,
    get_rag_prompt,
    get_summary_prompt,
)


def create_vector_store(text_chunks: List[Document]) -> FAISS:
    """Converts document text chunks into embeddings using HuggingFace

    (all-MiniLM-L6-v2) and stores them in an in-memory FAISS vector index.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = FAISS.from_documents(text_chunks, embeddings)
    return vector_store


def initialize_llm(
    temperature: float = 0.0, model_name: str = "gemini-2.5-flash"
) -> ChatGoogleGenerativeAI:
    """Initializes the Google Gemini LLM instance."""
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)


def invoke_chain_with_fallback(
    prompt_template: Any,
    input_vars: Dict[str, Any],
    temperature: float = 0.0,
    primary_model: str = "gemini-2.5-flash",
    fallback_model: str = "gemini-1.5-flash",
    max_retries: int = 3,
) -> str:
    """Invokes a LangChain prompt-LLM chain with primary model (gemini-2.5-flash)

    and automatic retry with exponential backoff & fallback to secondary model
    (gemini-1.5-flash) if 429 rate limits are encountered.
    """
    models = [primary_model, fallback_model]
    last_exception = None

    for model_name in models:
        try:
            llm = initialize_llm(temperature=temperature, model_name=model_name)
            chain = prompt_template | llm
        except Exception as init_err:
            last_exception = init_err
            continue

        for attempt in range(max_retries):
            try:
                response = chain.invoke(input_vars)
                return (
                    response.content if hasattr(response, "content") else str(response)
                )
            except Exception as e:
                err_text = str(e).upper()
                last_exception = e
                if (
                    "429" in err_text
                    or "RESOURCE_EXHAUSTED" in err_text
                    or "QUOTA" in err_text
                    or "RATE_LIMIT" in err_text
                ):
                    # Exponential backoff pause: 3s, 6s, 10s
                    wait_time = (attempt + 1) * 3 + (2 if attempt > 0 else 0)
                    time.sleep(wait_time)
                else:
                    # Non-rate limit error, don't keep retrying this model
                    break

    raise RuntimeError(
        "⏳ Gemini API rate limit reached (Free Tier quota: 20 requests/min). Please wait ~20 seconds and try again."
    ) from last_exception


def calculate_confidence_score(distance: float) -> Tuple[float, str]:
    """Calculates a normalized confidence score percentage and category string

    (High, Medium, Low) based on FAISS L2/Cosine similarity distance.
    """
    confidence_pct = max(0.0, min(100.0, (1.0 - (distance / 2.0)) * 100.0))
    confidence_pct = round(confidence_pct, 1)

    if confidence_pct >= 75.0:
        level = "High"
    elif confidence_pct >= 50.0:
        level = "Medium"
    else:
        level = "Low"

    return confidence_pct, level


def query_rag_pipeline(
    vector_store: FAISS,
    user_question: str,
    top_k: int = 4,
    temperature: float = 0.0,
    doc_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Executes the RAG pipeline query with document filtering, fallback, and

    confidence calculation.
    """
    filter_dict = None
    if doc_filter and doc_filter != "All Documents":
        filter_dict = {"source": doc_filter}

    try:
        if filter_dict:
            results_with_scores = vector_store.similarity_search_with_score(
                user_question, k=top_k, filter=filter_dict
            )
        else:
            results_with_scores = vector_store.similarity_search_with_score(
                user_question, k=top_k
            )
    except Exception:
        raw_results = vector_store.similarity_search_with_score(
            user_question, k=top_k * 3
        )
        results_with_scores = [
            (doc, score)
            for doc, score in raw_results
            if not doc_filter
            or doc_filter == "All Documents"
            or doc.metadata.get("source") == doc_filter
        ][:top_k]

    if not results_with_scores:
        return {
            "answer": "I don't know based on the provided documents.",
            "sources": [],
            "avg_confidence": 0.0,
        }

    formatted_context_blocks = []
    source_metadata_list = []
    total_confidence = 0.0

    for doc, distance in results_with_scores:
        source_name = doc.metadata.get("source", "Unknown Document")
        page_num = doc.metadata.get("page", 1)

        pct, level = calculate_confidence_score(distance)
        total_confidence += pct

        source_metadata_list.append(
            {
                "source": source_name,
                "page": page_num,
                "content": doc.page_content,
                "distance": round(distance, 4),
                "confidence_pct": pct,
                "confidence_level": level,
            }
        )

        formatted_block = (
            f"[Source: {source_name} | Page: {page_num}]\n{doc.page_content}"
        )
        formatted_context_blocks.append(formatted_block)

    context_str = "\n\n---\n\n".join(formatted_context_blocks)
    avg_confidence = round(
        float(total_confidence / len(results_with_scores)), 1
    )

    rag_prompt = get_rag_prompt()
    answer_text = invoke_chain_with_fallback(
        prompt_template=rag_prompt,
        input_vars={"context": context_str, "input": user_question},
        temperature=temperature,
    )

    return {
        "answer": answer_text,
        "sources": source_metadata_list,
        "avg_confidence": avg_confidence,
    }


def generate_document_summary(
    chunks: List[Document], max_chunks: int = 20, temperature: float = 0.2
) -> str:
    """Generates a structured executive summary across uploaded document

    chunks.
    """
    if not chunks:
        return "No document text available to summarize."

    selected_chunks = chunks[:max_chunks]
    context_str = "\n\n".join(
        [
            f"[Source: {c.metadata.get('source', 'Doc')}, Page {c.metadata.get('page', 1)}]\n{c.page_content}"
            for c in selected_chunks
        ]
    )

    summary_prompt = get_summary_prompt()
    return invoke_chain_with_fallback(
        prompt_template=summary_prompt,
        input_vars={"context": context_str},
        temperature=temperature,
    )


def generate_document_comparison(
    chunks: List[Document], max_chunks: int = 25, temperature: float = 0.2
) -> str:
    """Generates a multi-document comparison matrix across all uploaded

    documents.
    """
    if not chunks:
        return "No documents available for comparison."

    selected_chunks = chunks[:max_chunks]
    context_str = "\n\n---\n\n".join(
        [
            f"[Document: {c.metadata.get('source', 'Doc')} | Page {c.metadata.get('page', 1)}]\n{c.page_content}"
            for c in selected_chunks
        ]
    )

    comparison_prompt = get_comparison_prompt()
    return invoke_chain_with_fallback(
        prompt_template=comparison_prompt,
        input_vars={"context": context_str},
        temperature=temperature,
    )


def clean_json_response(response_text: str) -> str:
    """Cleans LLM response string to extract pure JSON array content."""
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()


def extract_key_topics(
    chunks: List[Document], max_chunks: int = 15, temperature: float = 0.2
) -> List[str]:
    """Extracts top 5 key topics from uploaded documents."""
    if not chunks:
        return []

    selected_chunks = chunks[:max_chunks]
    context_str = "\n\n".join([c.page_content for c in selected_chunks])

    key_topics_prompt = get_key_topics_prompt()
    try:
        raw_content = invoke_chain_with_fallback(
            prompt_template=key_topics_prompt,
            input_vars={"context": context_str},
            temperature=temperature,
        )
        json_str = clean_json_response(raw_content)
        topics = json.loads(json_str)
        return topics if isinstance(topics, list) else []
    except Exception:
        return []


def generate_quiz(
    chunks: List[Document],
    num_questions: int = 10,
    max_chunks: int = 10,
    temperature: float = 0.3,
) -> List[Dict[str, Any]]:
    """Generates a multiple-choice quiz based on document text."""
    if not chunks:
        return []

    effective_max_chunks = max(max_chunks, min(len(chunks), num_questions * 2))
    selected_chunks = chunks[:effective_max_chunks]
    context_str = "\n\n".join([c.page_content for c in selected_chunks])

    quiz_prompt = get_quiz_prompt()
    try:
        raw_content = invoke_chain_with_fallback(
            prompt_template=quiz_prompt,
            input_vars={
                "context": context_str,
                "num_questions": num_questions,
            },
            temperature=temperature,
        )
        json_str = clean_json_response(raw_content)
        quiz_data = json.loads(json_str)
        return quiz_data if isinstance(quiz_data, list) else []
    except Exception:
        return []


def generate_flashcards(
    chunks: List[Document],
    num_cards: int = 10,
    max_chunks: int = 10,
    temperature: float = 0.3,
) -> List[Dict[str, Any]]:
    """Generates educational flashcards (concept & definition) from document

    text.
    """
    if not chunks:
        return []

    effective_max_chunks = max(max_chunks, min(len(chunks), num_cards * 2))
    selected_chunks = chunks[:effective_max_chunks]
    context_str = "\n\n".join([c.page_content for c in selected_chunks])

    flashcard_prompt = get_flashcard_prompt()
    try:
        raw_content = invoke_chain_with_fallback(
            prompt_template=flashcard_prompt,
            input_vars={"context": context_str, "num_cards": num_cards},
            temperature=temperature,
        )
        json_str = clean_json_response(raw_content)
        card_data = json.loads(json_str)
        return card_data if isinstance(card_data, list) else []
    except Exception:
        return []
