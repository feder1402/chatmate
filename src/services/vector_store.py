import streamlit as st

import chromadb

from langchain_community.document_loaders import DirectoryLoader 
from langchain_community.document_loaders.text import TextLoader 
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
     
@st.cache_resource
def load_documents(knowledgeDirectoryPath):
    # st.write("Loading documents...")
    loader = DirectoryLoader(knowledgeDirectoryPath, glob="**/*.*", loader_cls=TextLoader) 
    loaded_docs = loader.load() 

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large") 
    #embeddings = SentenceTransformerEmbeddings(model_name="multi-qa-mpnet-base-cos-v1")

    # st.write("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100) 
    #splitter = SemanticChunker(embeddings)
    chunks = splitter.split_documents(loaded_docs) 

    # st.write("Creating embeddings...")
    persistent_client = chromadb.PersistentClient()
    collection_name = knowledgeDirectoryPath.replace("/", "_")
    collection = persistent_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
        )

    vector_store = Chroma(
        client=persistent_client,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    if collection.count() == 0:
        vector_store.add_documents(chunks)
    
    return vector_store

def retrieve_docs(query):
    vector_store = st.session_state["vector_store"]
    # Get documents similar to the query ith their scores
    docs_and_score = vector_store.similarity_search_with_score(query)
    
    # Remove duplicates and unrelated documents
    unique_docs = []
    unique_docs_and_score = []
    seen = set()
    ordered_byScore = sorted(docs_and_score, key=lambda x: x[1])
    for doc in ordered_byScore:
        content = doc[0].page_content
        score = doc[1]
        if score < 1.5 and content not in seen:
            unique_docs.append(content)
            unique_docs_and_score.append(doc)
            seen.add(content)
            
    context = "\n\n".join(unique_docs)
    
    return context, unique_docs_and_score

