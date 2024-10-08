import streamlit as st

model_list = st.session_state["config"].get("models")

if not model_list:
    st.error("Missing model information in the config.toml file.")
else:
    model_families = [k for k, _ in model_list.items()]
    default_ndx = model_families.index("openai")

    @st.fragment
    def select_model():
        modelfamily = st.selectbox("Model Family", model_families, index=default_ndx)
        model = st.selectbox("Model", model_list[modelfamily])

        return modelfamily, model