import streamlit as st
import platform
import pandas as pd
import os

from dotenv import load_dotenv, find_dotenv

from src.components.options.voice_panel import render_voice_panel
from src.services.RAG.vector_store import load_documents
from src.components.options.model_options import select_model
from src.components.options.prompt_options import prompt_options
from src.components.options.saved_queries import render_saved_queries
from src.components.chatbox import chatbox

current_platform = platform.system()

if current_platform == "Linux":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.set_page_config(layout="wide")

if "saved_query" not in st.session_state:
    st.session_state["saved_query"] = None
    
if "retrieval_score_threshold" not in st.session_state:
    st.session_state["retrieval_score_threshold"] = None
      
st.session_state["DocumentsPath"] = "knowledge/structured"

# Load API keys into the environment
_ = load_dotenv(find_dotenv()) # read local .env file

KnowledgeDirectoryPath = st.session_state["DocumentsPath"]

def refresh_docs(force_refresh=False):
    st.session_state["vector_store"] = load_documents(KnowledgeDirectoryPath, force_refresh=force_refresh)
    st.toast("Documents refreshed.", icon=":material/thumb_up:")

@st.dialog("Chunks", width="large")
def show_chunks():   
    vector_store = st.session_state["vector_store"]
    chunks = vector_store.get()
    st.write(f"Total documents: {len(chunks['documents'])}")
    documents = pd.DataFrame({
        "sources": [ os.path.basename(c["source"]) for c in chunks["metadatas"]],
        "size": [len(c) for c in chunks["documents"]],
        "documents": chunks["documents"],
        "ids": chunks["ids"]
    })
    documents.sort_values(by="sources", inplace=True)
    st.dataframe(documents)
    
if "vector_store" not in st.session_state:
    refresh_docs()
    
# Render UI
with st.sidebar:
    with st.expander("**Model**", icon="🤖", expanded=True):
        modelfamily, model = select_model()
    with st.expander("**Prompt**", icon="🎓"):
        instructions, scoped_answer, use_markdown, temperature, show_resource_links = prompt_options()
    with st.expander("**Documents**", icon="📁"):
        st.write("**Path:** " + st.session_state["DocumentsPath"])
        st.session_state["retrieval_score_threshold"] = st.slider("Retrieval score threshold", 0.0, 1.0, value=0.7, help="Maximum score to consider a document relevant during retrieval. Zero means most relevant.")
        col1, col2, col3 = st.columns([2, 4, 4])
        col2.button("Chunks", on_click=lambda: show_chunks())       
        col3.button("Reload", on_click=lambda: refresh_docs(True))
    with st.expander("Semantic caching", icon="🔍"):
        use_cache = st.toggle("Use semantic cache", value=True, help="Use semantic cache to speed up the search")
        similarity_threshold = 1.0
        if use_cache:
            similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, value=0.8, help="Minimum similarity to consider it a match. Lower values will return more results; 1.0 means exact match")           
    with st.expander("Voice", icon="🎤"):
        render_voice_panel()
    with st.expander("**Saved Queries**", icon="❓"):
        render_saved_queries()   
 
chatbox(modelfamily, model, instructions, scoped_answer, use_markdown, temperature, use_cache, similarity_threshold, show_resource_links)  

