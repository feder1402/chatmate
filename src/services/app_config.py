import streamlit as st
import tomli

def load_config():
    with open("config.toml", mode="rb") as fp:
        return tomli.load(fp)
    
if "config" not in st.session_state:
    st.session_state["config"] = load_config()    