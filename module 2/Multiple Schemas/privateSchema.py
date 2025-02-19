from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Define the main state schema (input/output of the graph)
class OverallState(TypedDict):
    foo: int  # This will be part of the final graph output

# Define the private state schema (only used between nodes)
class PrivateState(TypedDict):
    baz: int  # This is an intermediate value, not included in final output

# Node 1: Takes OverallState as input, outputs PrivateState
def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state['foo'] + 1}  # Creates intermediate value

# Node 2: Takes PrivateState as input, outputs OverallState
def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo": state['baz'] + 1}  # Converts private value back

# Build the graph
builder = StateGraph(OverallState)

# Add nodes
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

# Define execution flow
builder.add_edge(START, "node_1")  # Start → Node 1
builder.add_edge("node_1", "node_2")  # Node 1 → Node 2
builder.add_edge("node_2", END)  # Node 2 → End

# Compile the graph
graph = builder.compile()

# Display graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Invoke the graph with an initial state
result = graph.invoke({"foo": 10})

# Print final output
print("Final Output:", result)
