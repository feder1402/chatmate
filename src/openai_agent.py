# Bootstrap assistant
# Get API key and assistant ID from the environment variables
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

assistant_id = assistant_id = "asst_FaCBu1qjYHCrg1p29xTXmdyk"

# # Create an instance of the OpenAIAssistantV2Runnable class
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable as OpenAIAssistantRunnable

assistant = OpenAIAssistantRunnable(
    assistant_id=assistant_id,
    as_agent=True
)

from langchain.agents import AgentExecutor
executor = AgentExecutor(agent=assistant, tools=[])

def get_response(input):
    output = executor.invoke({"content": input})
    return output['output']

