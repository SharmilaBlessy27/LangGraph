from typing_extensions import TypedDict
import random
from langgraph.graph import StateGraph, START, END

# Define state schema using TypedDict
class TypedDictState(TypedDict):
    name: str
    mood: str  # Can be "happy" or "sad"

# Define nodes
def node_1(state: TypedDictState):
    print("--- Node 1 ---")
    return {"name": state["name"] + " is ... "}

def node_2(state: TypedDictState):
    print("--- Node 2 ---")
    return {"mood": "happy"}

def node_3(state: TypedDictState):
    print("--- Node 3 ---")
    return {"mood": "sad"}

# Define decision logic
def decide_mood(state: TypedDictState) -> str:
    return "node_2" if random.random() < 0.5 else "node_3"

# Build graph
builder = StateGraph(TypedDictState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile and run the graph
graph = builder.compile()
graph.invoke({"name": "Lance"})
