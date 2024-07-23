import streamlit as st

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness
)

def evaluations(response, query):
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
       
            
            
