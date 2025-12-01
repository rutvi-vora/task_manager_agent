from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from todoist_api_python.api import TodoistAPI

load_dotenv()

todoist_api_key = os.getenv("TODOIST_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

todoist = TodoistAPI(todoist_api_key)

@tool
def add_task(task, description=None):
    """
    Adds a new task to the user's task list. Use this when the user wants to add or create a new task.
    :return:
    """
    todoist.add_task(content=task, description=description)

tools = [add_task]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3, # to adjust model's creative behavior, 0 means more deterministic and less creative
    # 1 means more creative
    google_api_key=gemini_api_key
)

system_prompt = "You are a task management assistant that helps users organize their tasks using Todoist."
user_input = "add a new task to buy me a milk with the description to buy from the nearby store"

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", user_input),
    MessagesPlaceholder("agent_scratchpad")
])

# chain = prompt | llm | StrOutputParser()

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True)

# response = chain.invoke({"input": user_input})
response = agent_executor.invoke({"input": user_input})

print(response)
