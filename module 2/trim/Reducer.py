import os
import getpass
from pprint import pprint
from IPython.display import Image, display
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END

# Step 1: Set up API keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGCHAIN_API_KEY")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"

# Step 2: Define Message Filtering (Reducer)
def filter_messages(state: MessagesState):
    """
    This function filters out old messages, keeping only the last 2 messages.
    """
    # Remove all but the last 2 messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

# Step 3: Define Chat Model Node
llm = ChatOpenAI(model="gpt-4o")

def chat_model_node(state: MessagesState):    
    """
    This function takes filtered messages and generates a response.
    """
    return {"messages": [llm.invoke(state["messages"])]}

# Step 4: Build the Graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)  # First, filter messages
builder.add_node("chat_model", chat_model_node)  # Then, pass to the chat model
builder.add_edge(START, "filter")  # Start → Filter
builder.add_edge("filter", "chat_model")  # Filter → Chat Model
builder.add_edge("chat_model", END)  # Chat Model → End

# Compile the graph
graph = builder.compile()

# Display the graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Step 5: Define Messages (Long Conversation)
messages = [
    AIMessage(content="Hi.", name="Bot", id="1"),
    HumanMessage(content="Hi.", name="Lance", id="2"),
    AIMessage(content="So you said you were researching ocean mammals?", name="Bot", id="3"),
    HumanMessage(content="Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"),
]

# 📌 Before Filtering: Messages in the Conversation
print("\n📌 Initial Messages:")
for m in messages:
     m.pretty_print()

# Step 6: Invoke the Graph
print("\n🤖 Running Chatbot with Message Filtering...")
output = graph.invoke({'messages': messages})

# Step 7: Print Filtered and Processed Messages
print("\n📝 Chatbot Response:")
for m in output['messages']:
     m.pretty_print()
