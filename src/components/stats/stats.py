import streamlit as st
import os

from streamlit_feedback import streamlit_feedback

from src.components.stats.evaluations import evaluations

def show_stats(response, elapsed_time, model, query):           
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Time", f"{elapsed_time:.2f}s")
    if response["cached"]:
        col2.metric("Cached", "True")
        col3.metric("Similarity", f"{response['similarity']:.2f}")
        st.write("**Original Query:**", response['query'])
    else:
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
        with st.popover("more cool stuff...", help="See instructions and context sent to LLM, sources retrieved from vector store, and evaluation metrics for the results"):
            with st.container(height=400, border=False):
                tab1, tab2, tab3, tab4 = st.tabs([
                    " :classical_building: Sources ", 
                    " :robot_face: Instructions ", 
                    " :books: Context ", 
                    " :mortar_board: Evaluations "
                    ])
                with tab1:
                    retrieved_docs = []
                    for doc, score in response["docs_with_scores"]:
                        retrieved_docs.append({"score": f'{score:0.2f}', "source": os.path.basename(doc.metadata["source"]), "size": len(doc.page_content), "content": doc.page_content})
                    st.dataframe(retrieved_docs, use_container_width=True)
                with tab2:
                    st.write(response["instructions"])
                with tab3:
                    st.write(response["context"])
                with tab4:
                    st.button("Run evaluations", on_click=lambda: run_evaluations(tab4, response, query))

def run_evaluations(tab, response, query):
    with tab:
        evaluations(response, query)

