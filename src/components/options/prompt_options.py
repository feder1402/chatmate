import streamlit as st

@st.fragment
def prompt_options(system_prompt):
    instructions = st.text_area("instructions", system_prompt)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, help="Controls how deterministic the results would be")

    return instructions, temperature