from operator import add
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Custom reducer to safely combine lists
def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling cases where either or both inputs might be None."""
    if not left:
        left = []  # If left is None, use an empty list
    if not right:
        right = []  # If right is None, use an empty list
    return left + right  # Combine both lists safely

# Default state using the built-in `add` reducer
class DefaultState(TypedDict):
    foo: Annotated[list[int], add]

# Custom state using the `reduce_list` reducer
class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]

# Define a node that appends the value 2 to the state
def node_1(state):
    print("---Node 1---")
    return {"foo": [2]}

# === Test with Default Reducer ===
print("\n### Using Default Reducer ###")
builder = StateGraph(DefaultState)
builder.add_node("node_1", node_1)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)
graph = builder.compile()

# View graph
# display(Image(graph.get_graph().draw_mermaid_png()))

# Test invocation with foo=None (will raise TypeError)
try:
    print(graph.invoke({"foo": None}))
except TypeError as e:
    print(f"TypeError occurred: {e}")

# === Test with Custom Reducer ===
print("\n### Using Custom Reducer ###")
builder = StateGraph(CustomReducerState)
builder.add_node("node_1", node_1)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)
graph = builder.compile()

# View graph
# display(Image(graph.get_graph().draw_mermaid_png()))

# Test invocation with foo=None (should NOT raise an error)
try:
    print(graph.invoke({"foo": None}))  # Expected output: {'foo': [2]}
except TypeError as e:
    print(f"TypeError occurred: {e}")
