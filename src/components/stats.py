import streamlit as st

from streamlit_feedback import streamlit_feedback
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness
)

def show_stats(response, elapsed_time, model, query):           
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
                    retrieved_docs.append({"source": doc.metadata["source"], "score": f'{score:0.2f}', "size": len(doc.page_content), "content": doc.page_content})
                st.dataframe(retrieved_docs, use_container_width=True)
            with tab2:
                st.write(response["instructions"])
            with tab3:
                st.write(response["context"])
            with tab4:
                st.button("Run evaluations", on_click=lambda: evaluations(tab4, response, query))

                def evaluations(container, response, query):
                    with container:
                        data = {
                            "question": [query],
                            "answer": [response["content"]],
                            "contexts": [[response["context"]]],
                        }
                        dataset = Dataset.from_dict(data)
                        with st.spinner("Evaluating..."):
                            evals = evaluate(dataset, metrics=[answer_relevancy, faithfulness])
                            evals_df = [
                                ["answer_relevancy", f'{100*evals["answer_relevancy"]:0.0f}%', 'answer vs. question','Calculates the mean cosine similarity of the original question to a number of artifical questions generated from the answer'], 
                                ["faithfulness", f'{100*evals["faithfulness"]:0.0f}%', ' answer vs. context', 'Claims in the answer are identified and cross checked against the context to determine if they can be inferred from it']
                                ]
                            st.dataframe(evals_df, hide_index=True, column_config={1:"metric", 2:"value", 3:"compares", 4:"how is calculated"})
                            st.markdown("[Read about the metrics](https://docs.ragas.io/en/stable/concepts/metrics/index.html)")
       
            
            
