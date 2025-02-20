import os, getpass

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI

# Define arithmetic functions as tools
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b

# Define available tools
tools = [add, multiply, divide]

# Initialize the AI model
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, SystemMessage

# System message for AI behavior
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Define the assistant node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Initialize the graph builder
builder = StateGraph(MessagesState)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Set up memory for state tracking
memory = MemorySaver()
graph = builder.compile(interrupt_before=["assistant"], checkpointer=memory)

# Display the graph structure
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# Define initial input
initial_input = {"messages": [HumanMessage(content="Multiply 2 and 3")]}

# Thread ID for tracking execution
thread = {"configurable": {"thread_id": "1"}}

# Run the graph until the first interruption (before assistant executes)
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get the current state
state = graph.get_state(thread)
print("Current State:", state)

# Modify the state (change input)
graph.update_state(
    thread,
    {"messages": [HumanMessage(content="No, actually multiply 3 and 3!")]},
)

# Display the updated state
new_state = graph.get_state(thread).values
print("\nUpdated State Messages:")
for m in new_state['messages']:
    m.pretty_print()

# Continue execution with the modified state
for event in graph.stream(None, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()
