import streamlit as st

def set_message(text):
    st.session_state["saved_query"] = text
    
def render_saved_queries():    
   saved_queries = st.session_state["config"].get("saved_queries")    
   for saved_query in saved_queries:
       st.button(saved_query, on_click=set_message, args=[saved_query])
