import streamlit as st

import chromadb

from langchain_community.document_loaders import DirectoryLoader 
from langchain_community.document_loaders.text import TextLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
  
EMBEDDING_MODEL = "text-embedding-3-small"
  
#@st.cache_resource(show_spinner=True)
def load_documents(knowledgeDirectoryPath, force_refresh=False):
    persistent_client = chromadb.PersistentClient()
    collection_name = knowledgeDirectoryPath.replace("/", "_") + "_" + EMBEDDING_MODEL

    if force_refresh:
        persistent_client.delete_collection(collection_name)

    collection = persistent_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL) 

    vector_store = Chroma(
        client=persistent_client,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    if collection.count() == 0:
        loader = DirectoryLoader(knowledgeDirectoryPath, glob="**/*.*", loader_cls=TextLoader) 
        loaded_docs = loader.load() 

        splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=0) 
        #splitter = SemanticChunker(embeddings, breakpoint_threshold_type="gradient")

        chunks = splitter.split_documents(loaded_docs) 
    
        vector_store.add_documents(
            documents=chunks, 
            collection_name=collection_name
        )
        
    return vector_store

def retrieve_docs(query):
    vector_store: Chroma = st.session_state["vector_store"]
    # Get documents similar to the query ith their scores
    docs_and_score = vector_store.similarity_search_with_score(query)
    # docs = vector_store.max_marginal_relevance_search(query, k=2)
    # docs_and_score = [(doc, 0.20) for doc in docs]
    
    # Remove duplicates and unrelated documents
    unique_docs = []
    unique_docs_and_score = []
    seen = set()
    ordered_byScore = sorted(docs_and_score, key=lambda x: x[1])
    for doc in ordered_byScore:
        content = doc[0].page_content
        score = doc[1]
        if score < st.session_state["retrieval_score_threshold"] and content not in seen:
            unique_docs.append(content)
            unique_docs_and_score.append(doc)
            seen.add("<article>\n\n" + content + "\n\n</article>")
            
    context = "\n\n".join(unique_docs)
    
    return context, unique_docs_and_score

