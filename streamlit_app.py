import streamlit as st
import platform

current_platform = platform.system()

if current_platform == "Linux":
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.set_page_config(layout="wide")

if "saved_query" not in st.session_state:
    st.session_state["saved_query"] = None
    
if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None
    
st.session_state["DocumentsPath"] = "knowledge/structured"

# Load API keys into the environment
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

from src.services.vector_store import load_documents
from src.components.options.select_model import select_model
from src.components.options.prompt_options import prompt_options
from src.components.options.saved_queries import render_saved_queries
from src.components.chatbox import chatbox

KnowledgeDirectoryPath = st.session_state["DocumentsPath"]
st.session_state["vector_store"] = load_documents(KnowledgeDirectoryPath)

# Render UI
with st.sidebar:
    st.markdown("# 🧉 ChatMate")
    with st.expander("**Model**", icon="🤖", expanded=True):
        modelfamily, model = select_model()
    with st.expander("**Prompt**", icon="🎓"):
        instructions, scoped_answer, use_markdown, temperature = prompt_options()
    with st.expander("**Documents**", icon="📁"):
        st.write("**Path:** " + st.session_state["DocumentsPath"])
    with st.expander("**Saved Queries**", icon="❓"):
        render_saved_queries()   
 
chatbox(modelfamily, model, instructions, scoped_answer, use_markdown, temperature)  
    