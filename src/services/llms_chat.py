from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from src.services.semantic_cache import retrieve_from_cache, store_in_cache
from src.services.RAG.vector_store import retrieve_docs

SCOPED_PROMPT = """
If the answer to the user's question is not contained in the provided context, answer 🤷.
"""
# If the answer to the user question is not contained in the provided context and cannot be inferred from it, 
# answer 🤷.
# """

USE_MARKDOWN_PROMPT = """
Use Markdown to format your response.
"""

TRANSPARENT_CONTEXT = """
Do not mention the context in your answer.
"""

def get_fullInstructions(instructions, scoped_answer, use_markdown):
    full_instructions = instructions \
        + TRANSPARENT_CONTEXT \
        + (SCOPED_PROMPT if scoped_answer else "") \
        + (USE_MARKDOWN_PROMPT if use_markdown else "")
    return full_instructions

def get_prompt(instructions, scoped_answer, use_markdown, context):
    full_instructions = get_fullInstructions(instructions, scoped_answer, use_markdown)
    content = full_instructions \
        + "\n\n<context>\n\n" + context + "\n\n</context>\n\n"
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=content),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt

def get_response(query, modelfamily, model, instructions, scoped_answer, use_markdown, temperature, use_cache, similarity_threshold):    
    if use_cache:
        cached, similarity = retrieve_from_cache(query, similarity_threshold)
        if cached is not None:
            cached["cached"] = True
            cached["similarity"] = similarity
            return cached
    client = get_client(modelfamily, model, temperature)
    context, docs_with_scores = retrieve_docs(query)
    prompt = get_prompt(instructions, scoped_answer, use_markdown, context)

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
        "instructions": get_fullInstructions(instructions, scoped_answer, use_markdown),
        }
    
    if use_cache:
        store_in_cache(query, response)    
        
    return response

def get_client(model_family, model, temperature):
    if model_family == "openai":
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model=model, temperature=temperature)
    elif model_family == "anthropic":
        from langchain_anthropic import ChatAnthropic
        model = ChatAnthropic(model=model, temperature=temperature)
    else:
        raise ValueError(f"Model {model_family} not recognized")
    
    return model

def get_metadata(model_family, model, response):
    if model_family == "anthropic":
        usage = {k: v for k, v in response.response_metadata["usage"].items() if k in ("input_tokens", "output_tokens")}
    elif model_family == "openai":
        usage = {k: v for k, v in response.usage_metadata.items() if k in ("input_tokens", "output_tokens")}
    else:
        raise ValueError(f"Model family {model_family} not recognized")
    
    total_tokens = usage["input_tokens"] + usage["output_tokens"]

    return {"model": model, **usage, "total_tokens": total_tokens}
