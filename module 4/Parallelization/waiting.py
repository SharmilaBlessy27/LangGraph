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

# Define state structure properly
class State(TypedDict):
    state: Annotated[list, operator.add]  # Allows merging multiple values in parallel

# Node function: Appends a unique message to state
class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state": [self._value]}  # Returns list to be merged using `operator.add`

# Build the graph
builder = StateGraph(State)

# Initialize each node with a unique message
builder.add_node("a", ReturnNodeValue("A"))
builder.add_node("b", ReturnNodeValue("B"))
builder.add_node("b2", ReturnNodeValue("B2"))
builder.add_node("c", ReturnNodeValue("C"))
builder.add_node("d", ReturnNodeValue("D"))

# Define the execution flow
builder.add_edge(START, "a")  
builder.add_edge("a", "b")  # A → B
builder.add_edge("a", "c")  # A → C
builder.add_edge("b", "b2")  # B → B2
builder.add_edge(["b2", "c"], "d")  # Both B2 and C must complete before D
builder.add_edge("d", END)  # D → END

# Compile the graph
graph = builder.compile()

# Display the visual representation
display(Image(graph.get_graph().draw_mermaid_png()))

# Run the graph
graph.invoke({"state": []})
