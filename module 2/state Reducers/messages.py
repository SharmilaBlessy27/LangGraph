from typing import Annotated
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from IPython.display import Image

# Define a custom state (optional)
class CustomMessagesState(MessagesState):
    added_key_1: str  # Additional metadata fields can be added
    added_key_2: str

# Define a node that appends a new message
def node_1(state):
    print("--- Node 1 ---")
    new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")
    return {"messages": [new_message]}  # `add_messages` will automatically append it

# === Test `add_messages` Function Directly ===
# Initial messages
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model"),
    HumanMessage(content="I'm looking for information on marine biology.", name="Lance"),
]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# Manually test `add_messages` (it appends messages)
updated_messages = add_messages(initial_messages, new_message)
print("\nUpdated Messages:")
for msg in updated_messages:
    print(f"{msg.name}: {msg.content}")

# === Test in a LangGraph ===
builder = StateGraph(MessagesState)  # Use built-in MessagesState
builder.add_node("node_1", node_1)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)
graph = builder.compile()

# View graph
# display(Image(graph.get_graph().draw_mermaid_png()))

# Test invocation with initial messages
result = graph.invoke({"messages": initial_messages})
print("\nGraph Output:")
for msg in result["messages"]:
    print(f"{msg.name}: {msg.content}")
