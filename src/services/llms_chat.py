from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from src.services.vector_store import retrieve_docs

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

def get_prompt(instructions, scoped_answer, use_markdown, context):
    content = instructions \
        + TRANSPARENT_CONTEXT \
        + (SCOPED_PROMPT if scoped_answer else "") \
        + (USE_MARKDOWN_PROMPT if use_markdown else "") \
        + "\nContext:\n" + context 
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=content),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return prompt

def get_response(query, modelfamily, model, instructions, scoped_answer, use_markdown, temperature):    
    client = get_client(modelfamily, model, temperature)
    context, docs_with_scores = retrieve_docs(query)
    prompt = get_prompt(instructions, scoped_answer, use_markdown, context)

    chain = prompt | client
    response = chain.invoke({"messages": [HumanMessage(content=query)]})
    
    metadata = get_metadata(modelfamily, model, response)
    
    return {
        "content": response.content,
        "docs_with_scores": docs_with_scores,
        "metadata": metadata,
        "prompt": prompt,
        }
    
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
