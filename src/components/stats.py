import streamlit as st
from streamlit_feedback import streamlit_feedback

def show_stats(response, elapsed_time, model):           
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Time", f"{elapsed_time:.2f}s")
    col2.metric("Input Tokens", response['metadata']['input_tokens'])
    col3.metric("Output Tokens", response['metadata']['output_tokens'])
    col4.metric("Total Tokens", response['metadata']['total_tokens'])
    
    with col1:
        st.markdown("**Model:** " + model)
    with col2:
        feedback = streamlit_feedback(
            feedback_type="thumbs", 
            optional_text_label="[Optional] Please, provide an explanation"
            )            
    #with st.expander("Stats", expanded=False):
    with st.popover("more...", help="Show prompt sent and sources retrieved"):
        tab1, tab2 = st.tabs(["Prompt", "Sources"])

        with tab1:
            with st.container(height=400, border=False):
                st.write(response["prompt"][0].content)

        with tab2:
            retrieved_docs = []
            for doc, score in response["docs_with_scores"]:
                retrieved_docs.append({"source": doc.metadata["source"], "score": f'{score:0.2f}', "Length": len(doc.page_content), "content": doc.page_content})
            st.dataframe(retrieved_docs, use_container_width=True)