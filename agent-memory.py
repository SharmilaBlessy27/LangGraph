import os, getpass
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image, display

# Set environment variables for API keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"


# Define arithmetic tools
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    return a / b

# Define available tools
tools = [add, multiply, divide]

# Initialize LLM with tool bindings
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# Import necessary modules


# System message to set assistant behavior
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Define assistant function
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}



# Define the computation graph
builder = StateGraph(MessagesState)

# Define nodes (work units)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges (control flow)
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,  # Routes to tools if a tool call is detected, otherwise ends
)
builder.add_edge("tools", "assistant")  # Loops back to assistant

# Add memory to the graph using a checkpointer

memory = MemorySaver()

# Compile the graph with memory support
react_graph_memory = builder.compile(checkpointer=memory)

# Assign a thread ID to retain memory across steps
config = {"configurable": {"thread_id": "1"}}

# First interaction: Adding 3 and 4
messages = [HumanMessage(content="Add 3 and 4.")]
print("Sending message to assistant:", messages[0].content)
messages = react_graph_memory.invoke({"messages": messages}, config)
for m in messages['messages']:
    print(m.content)
    m.pretty_print()

# Second interaction: Multiply the result by 2
messages = [HumanMessage(content="Multiply that by 2.")]
messages = react_graph_memory.invoke({"messages": messages}, config)
for m in messages['messages']:
    m.pretty_print()
