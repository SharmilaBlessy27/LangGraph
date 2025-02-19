import os, getpass
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image, display
from langchain_openai import ChatOpenAI
# Set environment variables for API keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# Enable LangSmith tracing for logging
_set_env("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"


# Define arithmetic functions as tools
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a and b."""
    return a / b

# List of tools the agent can use
tools = [add, multiply, divide]

# Initialize the chat model
llm = ChatOpenAI(model="gpt-4o")

# Bind tools to the LLM (sequential execution for accuracy)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)



# System message to guide the assistant
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Assistant node - runs the model with tools
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}



# Build the agent graph
builder = StateGraph(MessagesState)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define control flow edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)  # Routes to tools or ends process
builder.add_edge("tools", "assistant")  # Loops back to assistant

# Compile graph
react_graph = builder.compile()

# Visualize graph
display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

# Example query: chained operations
messages = [HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5")]
messages = react_graph.invoke({"messages": messages})

# Print responses
for m in messages['messages']:
    m.pretty_print()
