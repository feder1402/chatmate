from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from src.services.semantic_cache import retrieve_from_cache, store_in_cache
from src.services.RAG.vector_store import retrieve_docs

def get_prompt(instructions, context):
    content = instructions + "\n\n<context>\n\n" + context + "\n\n</context>\n\n"
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=content),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt

def get_response(query, modelfamily, model, instructions, temperature, use_cache, similarity_threshold):    
    try:
        if use_cache:
            cached, similarity = retrieve_from_cache(query, similarity_threshold)
            if cached is not None:
                cached["cached"] = True
                cached["similarity"] = similarity
                return cached
        client = get_client(modelfamily, model, temperature)

        context, docs_with_scores = retrieve_docs(query)
        prompt = get_prompt(instructions, context)

        chain = prompt | client
        response = chain.invoke({"messages": [HumanMessage(content=query)]})
        
        metadata = get_metadata(modelfamily, model, response)
        
        response =  {
            "content": response.content,
            "cached": False,
            "query": query,
            "docs_with_scores": docs_with_scores,
            "context": context,
            "metadata": metadata,
            "instructions": instructions,
            }
        
        if use_cache:
            store_in_cache(query, response)    
            
        return response
    except Exception as e:
        return {"error": f"Error: {e}"}    

def get_client(model_family, model, temperature) -> ChatOpenAI | ChatAnthropic:
    if model_family == "openai":
        model = ChatOpenAI(model=model, temperature=temperature)
    elif model_family == "anthropic":
        model = ChatAnthropic(model=model, temperature=temperature)
    elif model_family == "google":
        model = ChatGoogleGenerativeAI(model=model, temperature=temperature)
    elif model_family == "groq":
        model = ChatGroq(model=model, temperature=temperature)
    else:
        raise ValueError(f"Model {model_family} not recognized")
    
    return model

def get_metadata(model_family, model, response):
    if model_family == "anthropic":
        usage = {k: v for k, v in response.response_metadata["usage"].items() if k in ("input_tokens", "output_tokens")}
    elif model_family in ["openai", "google", "groq"]:
        usage = {k: v for k, v in response.usage_metadata.items() if k in ("input_tokens", "output_tokens")}
    else:
        raise ValueError(f"Model family {model_family} not recognized")
    
    total_tokens = usage["input_tokens"] + usage["output_tokens"]

    return {"model": model, **usage, "total_tokens": total_tokens}
