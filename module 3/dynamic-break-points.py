from IPython.display import Image, display
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import START, END, StateGraph

# Define the state structure for our graph
class State(TypedDict):
    input: str

# Step 1: Initial processing (dummy step)
def step_1(state: State) -> State:
    print("---Step 1---")
    return state

# Step 2: Conditional check - raise NodeInterrupt if input length > 5
def step_2(state: State) -> State:
    if len(state['input']) > 5:
        raise NodeInterrupt(f"Received input that is longer than 5 characters: {state['input']}")
    
    print("---Step 2---")
    return state

# Step 3: Final processing
def step_3(state: State) -> State:
    print("---Step 3---")
    return state

# Build the state graph
builder = StateGraph(State)

# Add nodes
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

# Define execution flow
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

# Set up memory for storing graph states
memory = MemorySaver()

# Compile the graph with memory
graph = builder.compile(checkpointer=memory)

# Display the graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Run the graph with an input that triggers the interruption
initial_input = {"input": "hello world"}
thread_config = {"configurable": {"thread_id": "1"}}

# Execute the graph until the first interruption
for event in graph.stream(initial_input, thread_config, stream_mode="values"):
    print(event)

# Inspect the graph state (should show it stopped at step_2)
state = graph.get_state(thread_config)
print("Next node to execute:", state.next)

# Show the interruption log
print("Logged interruptions:", state.tasks)

# Try resuming the graph (will still be interrupted unless state is modified)
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)

# Inspect the graph state again
state = graph.get_state(thread_config)
print("Next node after retry:", state.next)

# Update the state to a valid input (shorter than 5 characters)
graph.update_state(
    thread_config,
    {"input": "hi"},
)

# Resume execution with the new state
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)
