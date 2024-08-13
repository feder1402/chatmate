from langchain_anthropic import ChatAnthropic
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.services.semantic_cache import retrieve_from_cache, store_in_cache
from src.services.RAG.vector_store import retrieve_docs

USE_CONTEXT_PROMPT = """
You will be provided with a context, consisting of a couple of articles (delimited with XML tags) about the same topic.
First, find the answer to the user question in the context. 
Then, craft an action-oriented response based on the answer you found.
"""

SCOPED_PROMPT = """
If the answer to the user question is not contained in the context, answer 🤷.
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

SHOW_RESOURCE_LINKS_PROMPT = """
If available, include a link to any resource mentioned.
"""

def get_fullInstructions(instructions, scoped_answer, use_markdown, show_resource_links):
    full_instructions = instructions \
        + TRANSPARENT_CONTEXT \
        + (SCOPED_PROMPT if scoped_answer else "") \
        + (USE_MARKDOWN_PROMPT if use_markdown else "") \
        + (SHOW_RESOURCE_LINKS_PROMPT if show_resource_links else "") \
        + USE_CONTEXT_PROMPT 
    return full_instructions

def get_prompt(instructions, scoped_answer, use_markdown, show_resource_links, context):
    full_instructions = get_fullInstructions(instructions, scoped_answer, use_markdown, show_resource_links)
    content = full_instructions \
        + "\n\n<context>\n\n" + context + "\n\n</context>\n\n"
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=content),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt

def augment_query_generated(query, client):
    messages = [
        ("system", "You are a helpfull agent. Provide an example answer to the user question."),
        ("user", "{query}")
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | client
    response = chain.invoke({"query": query})
    return response.content    

def get_response(query, modelfamily, model, instructions, scoped_answer, use_markdown, temperature, use_cache, similarity_threshold, show_resource_links):    
    if use_cache:
        cached, similarity = retrieve_from_cache(query, similarity_threshold)
        if cached is not None:
            cached["cached"] = True
            cached["similarity"] = similarity
            return cached
    client = get_client(modelfamily, model, temperature)

    context, docs_with_scores = retrieve_docs(query)
    prompt = get_prompt(instructions, scoped_answer, use_markdown, show_resource_links, context)

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
        "instructions": get_fullInstructions(instructions, scoped_answer, use_markdown, show_resource_links),
        }
    
    if use_cache:
        store_in_cache(query, response)    
        
    return response

def get_client(model_family, model, temperature) -> ChatOpenAI | ChatAnthropic:
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
