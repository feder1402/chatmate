from openai import OpenAI
import numpy as np

client = OpenAI()

cache=[]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   embeddings = client.embeddings.create(input = [text], model=model)
   
   return embeddings.data[0].embedding

def retrieve_from_cache(query, similarity_threshold):
    query_embedding = get_embedding(query)
    best_match = (None, 0)
    for i, (doc, embedding) in enumerate(cache):
        similarity = cosine_similarity(query_embedding, embedding)
        if similarity > similarity_threshold and similarity > best_match[1]:
            best_match = ((doc, similarity))
        
    return best_match

def store_in_cache(query, response):
    query_embedding = get_embedding(query)
    cache.append((response, query_embedding))