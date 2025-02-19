from typing_extensions import TypedDict
from typing import Literal
import random
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Define the state structure
class MoodState(TypedDict):
    message: str

# Define nodes (functions that modify the state)
def start_node(state):
    print("---Start Node---")
    return {"message": state['message'] + " I feel"}

def happy_node(state):
    print("---Happy Node---")
    return {"message": state['message'] + " excited!"}

def sad_node(state):
    print("---Sad Node---")
    return {"message": state['message'] + " down."}

# Function to decide the next node (random choice between happy_node and sad_node)
def determine_feeling(state) -> Literal["happy_node", "sad_node"]:
    if random.random() < 0.5:  # 50% chance
        return "happy_node"
    return "sad_node"

# Create a graph builder
builder = StateGraph(MoodState)

# Add nodes to the graph
builder.add_node("start_node", start_node)
builder.add_node("happy_node", happy_node)
builder.add_node("sad_node", sad_node)

# Define edges (connections between nodes)
builder.add_edge(START, "start_node")  # Start at start_node
builder.add_conditional_edges("start_node", determine_feeling)  # Decide between happy_node or sad_node
builder.add_edge("happy_node", END)  # End if going to happy_node
builder.add_edge("sad_node", END)  # End if going to sad_node

# Compile the graph
graph = builder.compile()

# Visualize the graph (optional, works in Jupyter Notebook)
display(Image(graph.get_graph().draw_mermaid_png()))

# Run the graph with an initial state
result = graph.invoke({"message": "Hello, world."})

# Print the final output
print("\nFinal Output:", result)
