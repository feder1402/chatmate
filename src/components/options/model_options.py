import streamlit as st

model_list = {
    "openai": ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"],
    "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"]
    }

model_families = [k for k, _ in model_list.items()]
default_ndx = model_families.index("openai")

@st.experimental_fragment
def select_model():
    modelfamily = st.selectbox("Model Family", model_families, index=default_ndx)
    model = st.selectbox("Model", model_list[modelfamily])

    return modelfamily, model