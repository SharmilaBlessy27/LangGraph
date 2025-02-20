import os, getpass

# Set OpenAI API Key if not already set
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

# Custom sorting reducer to enforce a deterministic order of state updates
def sorting_reducer(left, right):
    """Combines and sorts the values in a list"""
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return sorted(left + right, reverse=False)  # Sort in ascending order

# Define state structure with sorting reducer
class State(TypedDict):
    state: Annotated[list, sorting_reducer]  # Ensures updates are sorted

# Node function: Returns a message
class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state": [self._value]}

# Build the state graph
builder = StateGraph(State)

# Define nodes
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("b2", ReturnNodeValue("I'm B2"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))

# Define flow
builder.add_edge(START, "a")  # Start → A
builder.add_edge("a", "b")     # A → B
builder.add_edge("a", "c")     # A → C
builder.add_edge("b", "b2")    # B → B2
builder.add_edge(["b2", "c"], "d")  # B2 & C → D
builder.add_edge("d", END)     # D → End

# Compile and visualize graph
graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

# Run the graph
graph.invoke({"state": []})
