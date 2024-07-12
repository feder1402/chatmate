import streamlit as st

from langchain_community.document_loaders import DirectoryLoader 
from langchain_community.document_loaders.text import TextLoader 
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings

msg = st.toast("Loading documents...")
knowledgeDirectoryPath = st.session_state["DocumentsPath"]
loader = DirectoryLoader(knowledgeDirectoryPath, glob="**/*.*", loader_cls=TextLoader) 
loaded_docs = loader.load() 

embeddings = OpenAIEmbeddings(model="text-embedding-3-large") 

msg.toast("Splitting documents...")
#splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100) 
splitter = SemanticChunker(embeddings)
chunks = splitter.split_documents(loaded_docs) 

msg.toast("Creating embeddings...")
vector_store = Chroma.from_documents(chunks, embeddings) 

msg.toast(":sunglasses: Done loading documents: ")

def retrieve_docs(query):
    # Get documents similar to the query ith their scores
    docs_and_score = vector_store.similarity_search_with_score(query, k=5)
    
    # Remove duplicates and unrelated documents
    unique_docs = []
    unique_docs_and_score = []
    seen = set()
    ordered_byScore = sorted(docs_and_score, key=lambda x: x[1])
    for doc in ordered_byScore:
        content = doc[0].page_content
        score = doc[1]
        if score < 1 and content not in seen:
            unique_docs.append(content)
            unique_docs_and_score.append(doc)
            seen.add(content)
            
    context = "\n\n".join(unique_docs)
    
    return context, unique_docs_and_score

