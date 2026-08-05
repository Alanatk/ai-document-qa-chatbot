"""
AI Document Assistant - Main Streamlit Application.
Features: Multi-document QA, HuggingFace embeddings, FAISS vector database,
Google Gemini 2.5 Flash LLM, source citations, confidence metrics,
document filtering, processing speed stats, key topic badges,
multi-document comparison matrix, raw chunk inspector, Markdown exports,
quiz & flashcard generators, and system configuration.
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

from rag_pipeline import (
    create_vector_store,
    extract_key_topics,
    generate_document_comparison,
    generate_flashcards,
    generate_quiz,
    generate_document_summary,
    query_rag_pipeline,
)
from styles import load_css
from utils import calculate_document_stats, process_uploaded_file

# =====================================================================
# 1. Environment & Page Setup
# =====================================================================
load_dotenv()

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


# =====================================================================
# 2. Session State Initialization
# =====================================================================
def initialize_session_state():
    """Initializes Streamlit session state variables."""
    defaults = {
        "chat_history": [],
        "vector_store": None,
        "processed_chunks": [],
        "documents_processed": False,
        "processing_time": 0.0,
        "extracted_topics": [],
        "doc_stats": {
            "total_documents": 0,
            "total_chunks": 0,
            "total_words": 0,
            "total_characters": 0,
            "total_size_mb": 0.0,
            "file_names": [],
        },
        "executive_summary": "",
        "document_comparison": "",
        "quiz_data": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "flashcard_data": [],
        "flashcard_index": 0,
        "flashcard_show_answer": False,
        "top_k": 4,
        "temperature": 0.0,
        "selected_doc_filter": "All Documents",
        "pending_prompt": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# =====================================================================
# 3. Sidebar UI & Document Upload Handler
# =====================================================================
def render_sidebar():
    """Renders the sidebar containing file uploader, progress stats, and quick

    actions.
    """
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <div class="sidebar-title">📚 AI Assistant</div>
                <div class="sidebar-subtitle">Document Intelligence & RAG</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 📂 Upload Center")
        uploaded_files = st.file_uploader(
            "Upload PDF, DOCX, or TXT documents",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Select one or more documents to process into the AI knowledge base.",
        )

        if uploaded_files:
            st.markdown(f"**Selected Files ({len(uploaded_files)}):**")
            for f in uploaded_files:
                st.caption(f"📄 {f.name}")

        st.markdown("---")

        if st.button(
            "🚀 Process Documents",
            type="primary",
            use_container_width=True,
        ):
            if not uploaded_files:
                st.warning("⚠️ Please upload at least one document first.")
            else:
                start_time = time.time()
                progress_bar = st.progress(0, text="Initializing pipeline...")
                all_chunks = []
                total_files = len(uploaded_files)

                for idx, uploaded_file in enumerate(uploaded_files):
                    step_pct = int(((idx + 0.5) / total_files) * 50)
                    progress_bar.progress(
                        step_pct, text=f"Parsing {uploaded_file.name}..."
                    )

                    chunks = process_uploaded_file(uploaded_file)
                    all_chunks.extend(chunks)

                progress_bar.progress(
                    65, text="Generating embeddings & FAISS index..."
                )
                vector_store = create_vector_store(all_chunks)

                progress_bar.progress(85, text="Extracting key topics...")
                topics = extract_key_topics(all_chunks)

                progress_bar.progress(95, text="Calculating stats...")
                stats = calculate_document_stats(all_chunks, uploaded_files)
                elapsed = round(time.time() - start_time, 2)

                st.session_state.vector_store = vector_store
                st.session_state.processed_chunks = all_chunks
                st.session_state.doc_stats = stats
                st.session_state.extracted_topics = topics
                st.session_state.processing_time = elapsed
                st.session_state.documents_processed = True
                st.session_state.executive_summary = ""
                st.session_state.document_comparison = ""
                st.session_state.quiz_data = []
                st.session_state.flashcard_data = []

                progress_bar.progress(100, text="Processing complete!")
                st.success(
                    f"✅ Knowledge base built in {elapsed}s ({stats['total_size_mb']} MB)!"
                )
                st.rerun()

        st.markdown("---")

        # Sidebar Stats Summary
        st.markdown("### 📊 Document Statistics")
        stats = st.session_state.doc_stats
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Documents", stats["total_documents"])
            st.metric("Words", f"{stats['total_words']:,}")
            if st.session_state.processing_time > 0:
                st.metric("Build Time", f"{st.session_state.processing_time}s")

        with col_s2:
            st.metric("Chunks", stats["total_chunks"])
            st.metric("Chars", f"{stats['total_characters']:,}")
            if stats["total_size_mb"] > 0:
                st.metric("Total Size", f"{stats['total_size_mb']} MB")

        st.markdown("---")

        # Chat Control Actions
        st.markdown("### 🛠️ Actions")
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        if st.session_state.chat_history:
            formatted_chat = "AI DOCUMENT ASSISTANT - CHAT TRANSCRIPT\n\n"
            for msg in st.session_state.chat_history:
                formatted_chat += f"[{msg['role'].upper()}]: {msg['content']}\n"
                if "avg_confidence" in msg and msg["avg_confidence"] > 0:
                    formatted_chat += (
                        f"(Confidence: {msg['avg_confidence']:.1f}%)\n"
                    )
                formatted_chat += "-" * 40 + "\n"

            st.download_button(
                "⬇️ Download Chat History",
                data=formatted_chat,
                file_name="chat_history.txt",
                mime="text/plain",
                use_container_width=True,
            )

        st.markdown(
            """
            <div class="footer-text">
                Powered by Google Gemini 2.5 Flash<br>
                LangChain • FAISS • HuggingFace
            </div>
            """,
            unsafe_allow_html=True,
        )


# =====================================================================
# 4. Tab 1: Chat Interface with Topic Badges & Document Search Filter
# =====================================================================
def render_chat_tab():
    """Renders the core interactive RAG Chat interface with key topic badges,

    document filtering, suggested prompts, source citations, and confidence
    indicators.
    """
    st.markdown("### 💬 Chat with your Documents")

    if not st.session_state.documents_processed:
        st.info(
            "👈 **Getting Started:** Upload your PDF, DOCX, or TXT documents using the sidebar and click **Process Documents**."
        )
        return

    # Document Search Filter Header
    stats = st.session_state.doc_stats
    doc_options = ["All Documents"] + stats["file_names"]

    col_flt, col_blank = st.columns([2, 1])
    with col_flt:
        selected_filter = st.selectbox(
            "🎯 Filter Search Target:",
            options=doc_options,
            index=0,
            help="Select 'All Documents' or target a specific file for your questions.",
        )
        st.session_state.selected_doc_filter = selected_filter

    # Render Automatic Key Topic Badges
    topics = st.session_state.extracted_topics
    if topics:
        st.markdown("##### 🏷️ Key Document Topics (Click to Explore):")
        topic_cols = st.columns(min(5, len(topics)))
        for i, t in enumerate(topics[:5]):
            with topic_cols[i]:
                if st.button(
                    f"🏷️ {t}", key=f"topic_btn_{i}", use_container_width=True
                ):
                    st.session_state.pending_prompt = f"Explain all key details and requirements regarding '{t}' in the documents."
                    st.rerun()

    st.markdown("##### 💡 Quick Prompts:")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("📝 Summarize Key Topics", use_container_width=True):
            st.session_state.pending_prompt = (
                "Summarize the main topics and key highlights of the document."
            )
            st.rerun()
    with col_p2:
        if st.button("📋 List Main Requirements", use_container_width=True):
            st.session_state.pending_prompt = (
                "List all core requirements, objectives, and key takeaways."
            )
            st.rerun()
    with col_p3:
        if st.button("🔤 Define Important Terms", use_container_width=True):
            st.session_state.pending_prompt = (
                "Extract and define the top important terms and concepts."
            )
            st.rerun()

    st.markdown("---")

    # Display Existing Chat Messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
                avg_conf = round(float(msg.get("avg_confidence", 0.0)), 1)
                badge_class = (
                    "badge-high"
                    if avg_conf >= 75
                    else "badge-medium"
                    if avg_conf >= 50
                    else "badge-low"
                )

                st.markdown(
                    f'<span class="badge-confidence {badge_class}">Confidence: {avg_conf:.1f}%</span>',
                    unsafe_allow_html=True,
                )

                with st.expander(
                    f"📄 View Sources ({len(msg['sources'])} retrieved chunks)"
                ):
                    for idx, src in enumerate(msg["sources"], 1):
                        conf_pct = round(float(src["confidence_pct"]), 1)
                        st.markdown(
                            f"""
                            <div class="source-box">
                                <strong>Chunk {idx}</strong> — <em>{src['source']} (Page {src['page']})</em><br>
                                <small>Match Confidence: {conf_pct:.1f}% ({src['confidence_level']}) | Distance: {src['distance']}</small>
                                <p style="margin-top: 6px; font-style: italic;">"{src['content']}"</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # Determine prompt from chat_input or pending quick prompt
    user_input = st.chat_input(
        "Ask a question based on your uploaded documents..."
    )

    if not user_input and st.session_state.pending_prompt:
        user_input = st.session_state.pending_prompt
        st.session_state.pending_prompt = ""

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents & generating answer..."):
                try:
                    result = query_rag_pipeline(
                        vector_store=st.session_state.vector_store,
                        user_question=user_input,
                        top_k=st.session_state.top_k,
                        temperature=st.session_state.temperature,
                        doc_filter=st.session_state.selected_doc_filter,
                    )

                    answer = result["answer"]
                    sources = result["sources"]
                    avg_conf = round(float(result["avg_confidence"]), 1)

                    st.markdown(answer)

                    if sources:
                        badge_class = (
                            "badge-high"
                            if avg_conf >= 75
                            else "badge-medium"
                            if avg_conf >= 50
                            else "badge-low"
                        )

                        st.markdown(
                            f'<span class="badge-confidence {badge_class}">Confidence: {avg_conf:.1f}%</span>',
                            unsafe_allow_html=True,
                        )

                        with st.expander(
                            f"📄 View Sources ({len(sources)} retrieved chunks)"
                        ):
                            for idx, src in enumerate(sources, 1):
                                conf_pct = round(
                                    float(src["confidence_pct"]), 1
                                )
                                st.markdown(
                                    f"""
                                    <div class="source-box">
                                        <strong>Chunk {idx}</strong> — <em>{src['source']} (Page {src['page']})</em><br>
                                        <small>Match Confidence: {conf_pct:.1f}% ({src['confidence_level']}) | Distance: {src['distance']}</small>
                                        <p style="margin-top: 6px; font-style: italic;">"{src['content']}"</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "avg_confidence": avg_conf,
                        }
                    )

                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")


# =====================================================================
# 5. Tab 2: Document Summary & Multi-Document Comparison Matrix
# =====================================================================
def render_summary_tab():
    """Renders Executive Summary & Multi-Document Comparison Matrix with MD/TXT

    export options.
    """
    st.markdown("### 📄 Executive Summary & Document Comparison")

    if not st.session_state.documents_processed:
        st.info(
            "👈 Upload and process documents first to generate executive summary or comparison."
        )
        return

    stats = st.session_state.doc_stats
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "✨ Generate Executive Summary",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Analyzing document content..."):
                try:
                    summary = generate_document_summary(
                        chunks=st.session_state.processed_chunks,
                        temperature=st.session_state.temperature,
                    )
                    st.session_state.executive_summary = summary
                    st.success("Executive summary generated!")
                except Exception as e:
                    st.warning(f"⚠️ {str(e)}")

    with col2:
        if stats["total_documents"] >= 2:
            if st.button("⚔️ Compare Documents", use_container_width=True):
                with st.spinner("Comparing uploaded documents..."):
                    try:
                        comp = generate_document_comparison(
                            chunks=st.session_state.processed_chunks,
                            temperature=st.session_state.temperature,
                        )
                        st.session_state.document_comparison = comp
                        st.success("Document comparison matrix generated!")
                    except Exception as e:
                        st.warning(f"⚠️ {str(e)}")
        else:
            st.caption(
                "💡 Upload 2 or more documents to unlock Multi-Document Comparison."
            )

    if st.session_state.executive_summary:
        st.markdown("---")
        st.markdown(st.session_state.executive_summary)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "⬇️ Download Summary (MD)",
                data=st.session_state.executive_summary,
                file_name="executive_summary.md",
                mime="text/markdown",
            )
        with col_d2:
            st.download_button(
                "⬇️ Download Summary (TXT)",
                data=st.session_state.executive_summary,
                file_name="executive_summary.txt",
                mime="text/plain",
            )

    if st.session_state.document_comparison:
        st.markdown("---")
        st.markdown(st.session_state.document_comparison)

        col_dc1, col_dc2 = st.columns(2)
        with col_dc1:
            st.download_button(
                "⬇️ Download Comparison (MD)",
                data=st.session_state.document_comparison,
                file_name="document_comparison.md",
                mime="text/markdown",
            )
        with col_dc2:
            st.download_button(
                "⬇️ Download Comparison (TXT)",
                data=st.session_state.document_comparison,
                file_name="document_comparison.txt",
                mime="text/plain",
            )


# =====================================================================
# 6. Tab 3: Interactive Quiz Generator with MD/TXT Export
# =====================================================================
def render_quiz_tab():
    """Renders the interactive Quiz Generator tab with MD/TXT export support."""
    st.markdown("### ❓ Interactive Quiz Generator")

    if not st.session_state.documents_processed:
        st.info(
            "👈 Upload and process documents first to generate a knowledge quiz."
        )
        return

    col_cfg, col_btn = st.columns([2, 1])
    with col_cfg:
        num_q = st.number_input(
            "Number of Questions (e.g. 5, 10, 20, 50, 100)",
            min_value=3,
            max_value=100,
            value=10,
            step=1,
            help="Select how many questions to generate (up to 100).",
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🎲 Generate New Quiz", type="primary", use_container_width=True
        ):
            with st.spinner(
                f"Creating custom {num_q}-question quiz from documents..."
            ):
                try:
                    quiz_data = generate_quiz(
                        chunks=st.session_state.processed_chunks,
                        num_questions=int(num_q),
                        temperature=0.3,
                    )
                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    if not quiz_data:
                        st.warning(
                            "⚠️ Unable to structure quiz format from LLM output. Please try generating again."
                        )
                    else:
                        st.success(
                            f"Generated {len(quiz_data)} questions successfully!"
                        )
                except Exception as e:
                    st.warning(f"⚠️ {str(e)}")

    if st.session_state.quiz_data:
        st.markdown("---")

        formatted_quiz_text = "# AI DOCUMENT ASSISTANT - GENERATED QUIZ\n\n"
        for idx, q in enumerate(st.session_state.quiz_data, 1):
            formatted_quiz_text += f"### Q{idx}. {q['question']}\n"
            for opt in q.get("options", []):
                formatted_quiz_text += f"- {opt}\n"
            formatted_quiz_text += f"\n**Answer Key:** `{q.get('answer', '')}`\n"
            formatted_quiz_text += (
                f"*Explanation:* {q.get('explanation', '')}\n\n---\n\n"
            )

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.download_button(
                "⬇️ Download Quiz & Answer Key (MD)",
                data=formatted_quiz_text,
                file_name="generated_quiz.md",
                mime="text/markdown",
            )
        with col_q2:
            st.download_button(
                "⬇️ Download Quiz (TXT)",
                data=formatted_quiz_text,
                file_name="generated_quiz.txt",
                mime="text/plain",
            )

        st.markdown("---")

        with st.form("quiz_form"):
            for idx, q in enumerate(st.session_state.quiz_data, 1):
                st.markdown(
                    f"""
                    <div class="quiz-card">
                        <div class="quiz-question">Q{idx}. {q['question']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                selected_opt = st.radio(
                    f"Select answer for Question {idx}:",
                    options=q.get("options", []),
                    key=f"quiz_opt_{idx}",
                )
                st.session_state.quiz_answers[idx] = selected_opt
                st.markdown("<br>", unsafe_allow_html=True)

            submit_quiz = st.form_submit_button(
                "🎯 Submit Quiz Answers", use_container_width=True
            )

            if submit_quiz:
                st.session_state.quiz_submitted = True

        if st.session_state.quiz_submitted:
            st.markdown("---")
            st.markdown("### 🏆 Quiz Results")
            score = 0
            total = len(st.session_state.quiz_data)

            for idx, q in enumerate(st.session_state.quiz_data, 1):
                user_ans = st.session_state.quiz_answers.get(idx, "")
                correct_ans = q.get("answer", "")
                is_correct = user_ans.strip() == correct_ans.strip()

                if is_correct:
                    score += 1
                    st.success(
                        f"**Q{idx}: Correct!** Selected: `{user_ans}`\n\n💡 *Explanation:* {q.get('explanation', '')}"
                    )
                else:
                    st.error(
                        f"**Q{idx}: Incorrect.** Your Choice: `{user_ans}` | Correct Answer: `{correct_ans}`\n\n💡 *Explanation:* {q.get('explanation', '')}"
                    )

            final_pct = round((score / total) * 100, 1)
            st.balloons()
            st.metric(
                "Final Score",
                f"{score} / {total}",
                delta=f"{final_pct}% Correct",
            )


# =====================================================================
# 7. Tab 4: Interactive Flashcards with TXT Export
# =====================================================================
def render_flashcards_tab():
    """Renders the interactive Flashcards study tab with export support."""
    st.markdown("### 🧠 Concept Flashcards")

    if not st.session_state.documents_processed:
        st.info("👈 Upload and process documents first to generate flashcards.")
        return

    col_cfg, col_btn = st.columns([2, 1])
    with col_cfg:
        num_cards = st.number_input(
            "Number of Flashcards (e.g. 5, 10, 25, 50, 100)",
            min_value=3,
            max_value=100,
            value=10,
            step=1,
            help="Select how many flashcards to generate (up to 100).",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🎴 Generate Flashcards", type="primary", use_container_width=True
        ):
            with st.spinner(
                f"Extracting {num_cards} key terms & definitions..."
            ):
                try:
                    card_data = generate_flashcards(
                        chunks=st.session_state.processed_chunks,
                        num_cards=int(num_cards),
                        temperature=0.3,
                    )
                    st.session_state.flashcard_data = card_data
                    st.session_state.flashcard_index = 0
                    st.session_state.flashcard_show_answer = False
                    if not card_data:
                        st.warning(
                            "⚠️ Unable to parse flashcard format. Try regenerating."
                        )
                    else:
                        st.success(
                            f"Created {len(card_data)} flashcards successfully!"
                        )
                except Exception as e:
                    st.warning(f"⚠️ {str(e)}")

    if st.session_state.flashcard_data:
        st.markdown("---")

        formatted_cards_text = "# AI DOCUMENT ASSISTANT - STUDY FLASHCARDS\n\n"
        for idx, card in enumerate(st.session_state.flashcard_data, 1):
            formatted_cards_text += f"### Card {idx}\n"
            formatted_cards_text += (
                f"**Concept / Term:** {card.get('concept', '')}\n\n"
            )
            formatted_cards_text += (
                f"**Definition:** {card.get('definition', '')}\n\n---\n\n"
            )

        st.download_button(
            "⬇️ Download Flashcards (MD)",
            data=formatted_cards_text,
            file_name="generated_flashcards.md",
            mime="text/markdown",
        )

        st.markdown("---")

        cards = st.session_state.flashcard_data
        idx = st.session_state.flashcard_index
        total_c = len(cards)
        current_card = cards[idx]

        col_prev, col_counter, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button(
                "⬅️ Previous",
                disabled=(idx == 0),
                use_container_width=True,
                key="fc_prev",
            ):
                st.session_state.flashcard_index -= 1
                st.session_state.flashcard_show_answer = False
                st.rerun()

        with col_counter:
            st.markdown(
                f"<h4 style='text-align: center; margin: 0; color: #f8fafc;'>Card {idx + 1} of {total_c}</h4>",
                unsafe_allow_html=True,
            )

        with col_next:
            if st.button(
                "Next ➡️",
                disabled=(idx == total_c - 1),
                use_container_width=True,
                key="fc_next",
            ):
                st.session_state.flashcard_index += 1
                st.session_state.flashcard_show_answer = False
                st.rerun()

        if st.session_state.flashcard_show_answer:
            st.markdown(
                f"""
                <div class="flashcard-box" style="border-color: #3b82f6; background: linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%);">
                    <div class="flashcard-title">💡 DEFINITION / ANSWER</div>
                    <div class="flashcard-content">{current_card.get('definition', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="flashcard-box">
                    <div class="flashcard-title">❓ CONCEPT / QUESTION</div>
                    <div class="flashcard-content">{current_card.get('concept', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(
            "🔄 Flip Flashcard (Show/Hide Answer)", use_container_width=True
        ):
            st.session_state.flashcard_show_answer = (
                not st.session_state.flashcard_show_answer
            )
            st.rerun()


# =====================================================================
# 8. Tab 5: Settings, System Status & Raw Chunk Inspector
# =====================================================================
def render_settings_tab():
    """Renders System Configuration, Parameters, API Health, and Raw Chunk

    Inspector.
    """
    st.markdown("### ⚙️ System Settings & Health")

    api_key = os.getenv("GOOGLE_API_KEY")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if api_key:
            st.success("✅ GOOGLE_API_KEY detected in environment.")
        else:
            st.error(
                "❌ GOOGLE_API_KEY missing! Please add it to your .env file."
            )

    with col_k2:
        if st.session_state.documents_processed:
            st.success("✅ FAISS Vector Index active & ready.")
        else:
            st.info("ℹ️ FAISS Vector Store pending document upload.")

    st.markdown("---")
    st.markdown("### 🎛️ Retrieval & Generation Controls")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        top_k = st.slider(
            "Top-k Retrieved Chunks",
            min_value=1,
            max_value=10,
            value=st.session_state.top_k,
            help="Number of document chunks passed to LLM context.",
        )
        st.session_state.top_k = top_k

    with col_p2:
        temp = st.slider(
            "LLM Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="0.0 = deterministic & factual. Higher values = creative.",
        )
        st.session_state.temperature = temp

    st.markdown("---")
    st.markdown("### 🤖 Model Specification")
    st.code(
        """
LLM Model:           Google Gemini 2.5 Flash (gemini-2.5-flash)
Embedding Model:     HuggingFace all-MiniLM-L6-v2 (384 Dimensions)
Vector Database:     FAISS (In-Memory CPU Index)
Text Splitter:       RecursiveCharacterTextSplitter (Size=1000, Overlap=200)
    """,
        language="yaml",
    )

    # Raw Document Chunks Inspector
    chunks = st.session_state.processed_chunks
    if chunks:
        st.markdown("---")
        with st.expander(
            f"🔍 Raw Document Chunks Inspector ({len(chunks)} Chunks Indexed)"
        ):
            st.caption(
                "Inspect the raw parsed text chunks stored inside FAISS vector database:"
            )
            for idx, c in enumerate(chunks, 1):
                src = c.metadata.get("source", "Unknown")
                page = c.metadata.get("page", 1)
                text_len = len(c.page_content)
                word_len = len(c.page_content.split())

                st.markdown(
                    f"**Chunk {idx}:** *{src}* (Page {page}) | `{text_len} chars` | `{word_len} words`"
                )
                st.code(c.page_content, language="markdown")


# =====================================================================
# 9. Main Application Runner
# =====================================================================
def main():
    """App entrypoint rendering top title, dashboard metrics, and navigation

    tabs.
    """
    render_sidebar()

    st.title("📚 AI Document Assistant")
    st.caption(
        "Interactive RAG Chatbot Powered by Google Gemini 2.5 Flash, LangChain & FAISS"
    )

    stats = st.session_state.doc_stats
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">📁</span>
                    <span class="stat-label">Active Documents</span>
                </div>
                <div class="stat-value">{stats['total_documents']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">🧩</span>
                    <span class="stat-label">Total Text Chunks</span>
                </div>
                <div class="stat-value">{stats['total_chunks']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">📝</span>
                    <span class="stat-label">Word Count</span>
                </div>
                <div class="stat-value">{stats['total_words']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">🔤</span>
                    <span class="stat-label">Character Count</span>
                </div>
                <div class="stat-value">{stats['total_characters']:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_chat, tab_summary, tab_quiz, tab_flashcard, tab_settings = st.tabs(
        [
            "💬 Chat",
            "📄 Summary",
            "❓ Quiz Generator",
            "🧠 Flashcards",
            "⚙️ Settings",
        ]
    )

    with tab_chat:
        render_chat_tab()

    with tab_summary:
        render_summary_tab()

    with tab_quiz:
        render_quiz_tab()

    with tab_flashcard:
        render_flashcards_tab()

    with tab_settings:
        render_settings_tab()


if __name__ == "__main__":
    main()