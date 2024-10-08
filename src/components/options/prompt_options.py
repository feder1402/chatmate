import streamlit as st

@st.fragment
def prompt_options():
    instructions = st.text_area("instructions")
    scoped_answer = st.toggle("Scope answer to context", True, help="Adds 'If the answer to the user's question is not contained in the provided context, answer 🤷.' to the instructions")
    use_markdown = st.toggle("Use Markdown in responses", True, help="Adds 'Use Markdown to format your response.' to the instructions")
    show_resource_links = st.toggle("Show resource links", True, help="Adds 'If available, include a link to every resource mentioned.' to the instructions")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, help="Controls how deterministic the results would be")

    return instructions, scoped_answer, use_markdown, temperature, show_resource_links