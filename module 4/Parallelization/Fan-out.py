import os, getpass

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

from IPython.display import Image, display
from typing import Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Annotated
import operator
# Define state structure
class State(TypedDict):
    state: Annotated[list, operator.add] 

# Node function: Returns a message
class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state": [self._value]}

builder = StateGraph(State)
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))

# Parallel execution (Fan-out and Fan-in)
builder.add_edge(START, "a")  
builder.add_edge("a", "b")  # A → B
builder.add_edge("a", "c")  # A → C
builder.add_edge("b", "d")  # B → D
builder.add_edge("c", "d")  # C → D
builder.add_edge("d", END)

# Compile and visualize graph
graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

# Run graph
graph.invoke({"state": []})