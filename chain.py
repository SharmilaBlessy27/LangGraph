import os
import getpass
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from IPython.display import Image, display
import re

# 🔑 Set OpenAI API Key
def _set_env(var: str):
    if var not in os.environ:
        os.environ[var] = getpass.getpass(f"Enter {var}: ")

_set_env("OPENAI_API_KEY")

# 🤖 Initialize OpenAI Model
llm = ChatOpenAI(model="gpt-4o")

# 🛠️ Define a Multiplication Tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# 🔗 Bind the tool to the LLM
llm_with_tools = llm.bind_tools([multiply])

# 📜 Define Message State
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# 💡 Define Tool-Calling LLM Logic
def tool_calling_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
# 🕸️ Build the LangGraph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", RunnableLambda(tool_calling_llm))
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# 📊 Display Graph Visualization
display(Image(graph.get_graph().draw_mermaid_png()))

# 💬 Test the Graph with Messages

# 1️⃣ Normal Chat Message
messages = graph.invoke({"messages": [HumanMessage(content="Hello!")]})
for m in messages['messages']:
    print(f"{m.name or 'User'}: {m.content}")



# 2️⃣ Multiplication Request
messages = graph.invoke({"messages": [HumanMessage(content="Multiply 50 by 7")]})
for m in messages['messages']:
    print(f"{m.name or 'User'}: {m.content}")
