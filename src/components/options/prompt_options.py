import streamlit as st

model_list = {
    "openai": ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"],
    "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"]
    }

model_families = [k for k, _ in model_list.items()]
default_ndx = model_families.index("openai")

@st.fragment
def prompt_options():
    instructions = st.text_area("instructions")
    scoped_answer = st.toggle("Scope answer to context", True, help="Adds 'If the answer to the user's question is not contained in the provided context, answer 🤷.' to the instructions")
    use_markdown = st.toggle("Use Markdown in responses", True, help="Adds 'Use Markdown to format your response.' to the instructions")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, help="Controls how deterministic the results would be")

    return instructions, scoped_answer, use_markdown, temperature