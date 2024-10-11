import streamlit as st
import platform

from dotenv import load_dotenv, find_dotenv
from src.services.app_config import load_config
from src.components.sidebar import refresh_docs, settings_panel
from src.components.chatbox import chatbox

st.set_page_config(layout="wide")

current_platform = platform.system()

if current_platform == "Linux":
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

if "config" not in st.session_state:
    st.session_state["config"] = load_config()

if "saved_query" not in st.session_state:
    st.session_state["saved_query"] = None
    
# Load API keys into the environment
_ = load_dotenv(find_dotenv())  # read local .env file

if "vector_store" not in st.session_state:
    refresh_docs()

# Render UI
with st.sidebar:
    modelfamily, model, instructions, temperature, use_cache, similarity_threshold = settings_panel()  

chatbox(modelfamily, model, instructions, temperature, use_cache, similarity_threshold)
