from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

# Step 1: Initial Messages
messages = [
    AIMessage(content="Hi.", name="Bot", id="1"),
    HumanMessage(content="Hi.", name="Lance", id="2"),
    AIMessage(content="So you said you were researching ocean mammals?", name="Bot", id="3"),
    HumanMessage(content="Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"),
]

# Step 2: Select Messages to Remove (First Two Messages: ID 1 & 2)
delete_messages = [RemoveMessage(id=m.id) for m in messages[-2:]]

# Step 3: Apply add_messages to Remove Messages
updated_messages = add_messages(messages, delete_messages)

# Step 4: Display Results
print("\nUpdated Messages After Removal:")
for msg in updated_messages:
    print(f"{msg.name} (ID: {msg.id}): {msg.content}")
