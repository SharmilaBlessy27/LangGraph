from operator import add
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Define the state with a reducer
class State(TypedDict):
    foo: Annotated[list[int], add]  # Uses 'add' to append new values instead of overwriting

# Define nodes that update the state
def node_1(state):
    print("---Node 1---")
    foo = state.get("foo", [])  # Ensure it's a list
    return {"foo": foo + [foo[-1] + 1] if foo else [1]}  # Handle None case

def node_2(state):
    print("---Node 2---")
    foo = state.get("foo", [])  
    return {"foo": foo + [foo[-1] + 1] if foo else [1]}

def node_3(state):
    print("---Node 3---")
    foo = state.get("foo", [])  
    return {"foo": foo + [foo[-1] + 1] if foo else [1]}

# Build the state graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Define branching logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile and visualize the graph
graph = builder.compile()


# Invoke the graph with an initial state
print(graph.invoke({"foo": [1]}))  # Expected Output: {'foo': [1, 2, 3, 3]}

# Handle case where 'foo' is None
try:
    print(graph.invoke({"foo": None}))
except TypeError as e:
    print(f"TypeError occurred: {e}")
