import os, getpass
from langchain_openai import ChatOpenAI
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Set OpenAI API Key
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# Define arithmetic tools
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

def add(a: int, b: int) -> int:
    """Add a and b."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b

# List of tools
tools = [add, multiply, divide]

# Initialize AI model
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# Define system message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Define assistant node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Create LangGraph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Enable breakpoint before tools execution
memory = MemorySaver()
graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)

# Display the graph
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# Input message
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

# Create a thread
thread = {"configurable": {"thread_id": "2"}}

# Run the graph until the first interruption (before calling tools)
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Ask for user approval
user_approval = input("Do you want to call the tool? (yes/no): ")

# Handle approval decision
if user_approval.lower() == "yes":
    # Continue execution if approved
    for event in graph.stream(None, thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
else:
    print("Operation cancelled by user.")
