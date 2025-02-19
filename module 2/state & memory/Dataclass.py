from dataclasses import dataclass
from langgraph.graph import StateGraph, START, END

# Define state schema using Dataclass
@dataclass
class DataclassState:
    name: str
    mood: str  # "happy" or "sad"

# Define node functions
def node_1(state: DataclassState):
    print("--- Node 1 ---")
    return {"name": state.name + " is ... "}

def node_2(state: DataclassState):
    print("--- Node 2 ---")
    return {}

def node_3(state: DataclassState):
    print("--- Node 3 ---")
    return {}

# Define conditional function
def decide_mood(state: DataclassState):
    return "node_2" if state.mood == "happy" else "node_3"

# Build graph
builder = StateGraph(DataclassState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile and run the graph
graph = builder.compile()
graph.invoke(DataclassState(name="Lance", mood="happy"))
