import streamlit as st

QUERIES = [
    "I'm a new associate. What should I do to be successful?",
    "I'm an experienced associate. How can I continue growing?",
    "How can I become a LegalShield associate?",
    "What are the associate levels?",
    "What are the key things to know about LegalShield?",
    "What is LegalShield story?",
    "What are the benefits of being an associate?",
    "Who is Darnell?",
    "What is the capital of Argentina?"
]

def set_message(text):
    st.session_state["saved_query"] = text
    
def render_saved_queries():        
   for saved_query in QUERIES:
       st.button(saved_query, on_click=set_message, args=[saved_query])
