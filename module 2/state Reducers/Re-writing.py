from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

# Initial messages
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
    HumanMessage(content="I'm looking for information on marine biology.", name="Lance", id="2"),
]

# New message (same ID as the second message)
new_message = HumanMessage(content="I'm looking for information on whales, specifically", name="Lance", id="2")

# Apply add_messages
updated_messages = add_messages(initial_messages, new_message)

# Display results
print("\nUpdated Messages:")
for msg in updated_messages:
    print(f"{msg.name} (ID: {msg.id}): {msg.content}")
