import os, getpass
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from IPython.display import Image, display

# === Set API Key ===
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# === Define Arithmetic Tools ===
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b

tools = [add, multiply, divide]

# === Initialize LLM with Tools ===
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# === System Message ===
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# === Assistant Node ===
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# === Build Graph ===
builder = StateGraph(MessagesState)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges (control flow)
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# === Initialize Memory Saver ===
memory = MemorySaver()
graph = builder.compile(checkpointer=MemorySaver())

# === Visualize Graph ===
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# === Run the Graph ===
initial_input = {"messages": [HumanMessage(content="Multiply 2 and 3")]}
thread = {"configurable": {"thread_id": "1"}}

for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# === Browsing State History ===
all_states = [s for s in graph.get_state_history(thread)]
print(f"Total states: {len(all_states)}")

# Get a previous state (before the last step)
to_replay = all_states[-2]

# === Replaying Execution from a Past State ===
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event['messages'][-1].pretty_print()

# === Forking Execution ===
# Modify the previous state and run with new input
fork_config = graph.update_state(
    to_replay.config,
    {"messages": [HumanMessage(content='Multiply 5 and 3', 
                               id=to_replay.values["messages"][0].id)]},
)

# Run the forked execution
for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get the final state after forking
graph.get_state({'configurable': {'thread_id': '1'}})
