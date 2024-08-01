import streamlit as st

QUERIES = [
    "I'm a new associate. What should I do to be successful?",
    "I'm an experienced associate. How can I continue growing?",
    "How can I become a LegalShield associate?",
    "What incentives and promotions are available for associates?",
    "I have a meeting with a potential client. What should I do?",
    "I have a call with a potential client. What should I do?",
    "How can I help my customers understand the value of LegalShield services?",
    "What are the associate levels?",
    "What is the prospect mobile app?",
    "How do you save a member whose plan is going to be canceled?",
    "What are the key things to know about LegalShield?",
    "What is LegalShield story?",
    "What are the benefits of being an associate?",
    "What is Darnell story?",
    "What is the capital of Argentina?",
    "what would you say to a customer who is planning to cancel his plan?"
]

def set_message(text):
    st.session_state["saved_query"] = text
    
def render_saved_queries():        
   for saved_query in QUERIES:
       st.button(saved_query, on_click=set_message, args=[saved_query])
