import streamlit as st

st.set_page_config(layout="wide")

if "saved_query" not in st.session_state:
    st.session_state["saved_query"] = None
    
st.session_state["DocumentsPath"] = "knowledge/structured"

# Load API keys into the environment
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

from src.components.options.select_model import select_model
from src.components.options.prompt_options import prompt_options
from src.components.options.saved_queries import render_saved_queries
from src.components.chatbox import chatbox

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
    