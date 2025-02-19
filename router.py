import os
import getpass
import re
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from IPython.display import Image, display

# 🔑 Set OpenAI API Key
def _set_env(var: str):
    if var not in os.environ:
        os.environ[var] = getpass.getpass(f"Enter {var}: ")

_set_env("OPENAI_API_KEY")

# 🤖 Initialize OpenAI Model
llm = ChatOpenAI(model="gpt-4o")

# 🛠️ Define Multiplication and Division Tools
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

# 🔗 Bind Tools to LLM
llm_with_tools = llm.bind_tools([multiply, divide])

# 📜 Define Message State
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# 💡 Define Tool-Calling Logic
def tool_calling_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# 🕸️ Build the Graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", RunnableLambda(tool_calling_llm))
builder.add_node("tools", ToolNode([multiply, divide]))

# 📌 Routing Logic
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", END)

# 📊 Compile and Display Graph
graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

# 💬 Test Cases
test_cases = [
    "Hello! tell me one joke",               # Normal chat
    "Multiply 50 by 7",     # Multiplication
    "What is 20 times 5?",  # Multiplication
    "Divide 100 by 4",      # Division
    "Can you divide 10 / 2?", # Division
    "Divide 10 by 2",       # Division by zero
]

for test in test_cases:
    print(f"\n👤 **User:** {test}")
    messages = graph.invoke({"messages": [HumanMessage(content=test)]})
    for m in messages['messages']:
        print(f"🤖 **Chatbot:** {m.content}")
