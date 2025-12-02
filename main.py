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

@tool
def show_tasks():
    """
    Shows the user's current tasks. Use this when the user wants to see their task list.
    :return:
    """
    results_paginator = todoist.get_tasks()
    tasks = []
    for task_list in results_paginator:
        for task in task_list:
            tasks.append(task.content)
    return tasks

tools = [add_task, show_tasks]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3, # to adjust model's creative behavior, 0 means more deterministic and less creative
    # 1 means more creative
    google_api_key=gemini_api_key
)

system_prompt = """You are a helpful assistant. You will help the user add tasks. 
You will help the user show existing tasks. If user asks to show the tasks: for example, 'show all the tasks' print
out the tasks to the user. Print them in a bullet list format"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
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
# response = agent_executor.invoke({"input": user_input})

# print(response)
history = []
while True:
    user_input = input("You: ")
    response = agent_executor.invoke({"input": user_input, "history": history})
    print(response)
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response['output']))
