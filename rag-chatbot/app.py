import os
import tempfile
import streamlit as st
from rag_engine import RAGEngine

st.set_page_config(
    page_title="RAG Chatbot - PDF Q&A",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
    .user-msg {
        background: #1a1a2e;
        border-left: 3px solid #00d2ff;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #e0e0e0;
    }
    .bot-msg {
        background: #16213e;
        border-left: 3px solid #00e676;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: #e0e0e0;
    }
    .source-box {
        background: #0a0a1a;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 6px;
        font-size: 0.85em;
        margin: 4px 0;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdfs_loaded" not in st.session_state:
    st.session_state.pdfs_loaded = False

if "load_info" not in st.session_state:
    st.session_state.load_info = {}

with st.sidebar:
    st.title("📄 RAG Chatbot")
    st.caption("Upload PDFs → Ask Questions → Get Answers")
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("🚀 Process PDFs", type="primary", use_container_width=True):
            with st.spinner("Processing... PDFs padh raha hoon..."):
                temp_paths = []
                for uploaded_file in uploaded_files:
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    temp_paths.append(temp_path)

                result = st.session_state.rag_engine.load_pdfs(temp_paths)

                if result["status"] == "success":
                    st.session_state.pdfs_loaded = True
                    st.session_state.load_info = result
                    st.session_state.chat_history = []
                    st.success(f"✅ Done! {result['total_pages']} pages → {result['total_chunks']} chunks")
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")

    if st.session_state.pdfs_loaded:
        st.divider()
        st.markdown("### 📊 Stats")
        info = st.session_state.load_info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pages", info.get("total_pages", 0))
        with col2:
            st.metric("Chunks", info.get("total_chunks", 0))

    if st.session_state.pdfs_loaded:
        st.divider()
        if st.button("🗑️ Reset Everything", use_container_width=True):
            st.session_state.rag_engine.reset()
            st.session_state.chat_history = []
            st.session_state.pdfs_loaded = False
            st.session_state.load_info = {}
            st.rerun()

    st.divider()
    st.markdown("""
    ### 💡 How it works
    1. **Upload** any PDF file(s)
    2. Click **Process PDFs**
    3. **Ask questions** about the content
    4. Get **AI-powered answers** with source references

    ### 🛠️ Tech Stack
    - LangChain + ChromaDB
    - OpenAI GPT-3.5
    - Streamlit UI
    """)

st.title("💬 Chat with your PDFs")

if not st.session_state.pdfs_loaded:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; color: #888;">
        <h2>📄 Upload a PDF to get started</h2>
        <p>Use the sidebar to upload your PDF files, then ask any question about them.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="user-msg">🧑 <b>You:</b> {chat["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-msg">🤖 <b>Answer:</b> {chat["answer"]}</div>', unsafe_allow_html=True)

        if chat.get("sources"):
            with st.expander(f"📚 Sources ({len(chat['sources'])} chunks used)"):
                for i, source in enumerate(chat["sources"], 1):
                    st.markdown(
                        f'<div class="source-box">'
                        f'<b>Chunk {i}</b> | Page: {source["page"]} | File: {source["file"]}<br>'
                        f'{source["content"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    question = st.chat_input("Apna sawaal puchho...")

    if question:
        with st.spinner("Soch raha hoon... 🤔"):
            result = st.session_state.rag_engine.ask(question)

        st.session_state.chat_history.append({
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        })

        st.rerun()