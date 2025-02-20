import os
import getpass
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from typing import Literal, TypedDict

# Set OpenAI API Key
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# MongoDB Connection (Replace with your actual MongoDB URI)
MONGODB_URI = "mongodb://localhost:27017/"
mongodb_client = MongoClient(MONGODB_URI)

# Initialize MongoDB Checkpointer
checkpointer = MongoDBSaver(mongodb_client)

# Define a Tool (Weather API Simulation)
@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this tool to get weather information for NYC or SF."""
    if city == "nyc":
        return "It might be cloudy in NYC."
    elif city == "sf":
        return "It's always sunny in SF."
    else:
        raise AssertionError("Unknown city")

# Define Tools & AI Model
tools = [get_weather]
model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Define the State for the Agent
class AgentMemory(TypedDict):
    messages: list

# Create a StateGraph
builder = StateGraph(AgentMemory)

# Add AI Node
builder.add_node("agent", model)

# Add Edge to Handle Responses
builder.set_entry_point("agent")

# Compile the Graph
graph = builder.compile(checkpointer=checkpointer)

# Define a session (thread_id ensures persistence across interactions)
config = {"configurable": {"thread_id": "1"}}

# User interacts with the agent
response = graph.invoke({"messages": [("human", "What's the weather in SF?")]}, config)
print(response)
