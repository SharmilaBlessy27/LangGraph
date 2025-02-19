import os
import getpass
from pprint import pprint
from IPython.display import Image, display
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
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

# Step 2: Define Chat Model
llm = ChatOpenAI(model="gpt-4o")

# Step 3: Define Chat Node with Message Trimming
def chat_model_node(state: MessagesState):
    # Trim messages to a max of 100 tokens
    messages = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",  # Keep the last messages until the limit
        token_counter=ChatOpenAI(model="gpt-4o"),
        allow_partial=False  # Don't allow incomplete messages
    )
    return {"messages": [llm.invoke(messages)]}

# Step 4: Build the Graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

# Compile the graph
graph = builder.compile()

# Display the graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Step 5: Create Initial Messages (Simulating a Long Conversation)
messages = [
    AIMessage(content="Hi, how can I help you today?", name="Bot"),
    HumanMessage(content="I want to learn about ocean mammals.", name="Lance"),
    AIMessage(content="Great! Do you already know about whales?", name="Bot"),
    HumanMessage(content="Yes, but I want to learn about others too.", name="Lance"),
    AIMessage(content="You might be interested in sea otters, dolphins, and narwhals.", name="Bot"),
    HumanMessage(content="Tell me more about Narwhals!", name="Lance"),
]

# Step 6: Trim Messages Before Sending to AI
trimmed_messages = trim_messages(
    messages,
    max_tokens=10,  # Only keep messages within 100 tokens
    strategy="last",
    token_counter=ChatOpenAI(model="gpt-4o"),
    allow_partial=False
)

# Print Trimmed Messages
print("\n✂️ Trimmed Messages (Before Sending to AI):")
for m in trimmed_messages:
    m.pretty_print()

# Step 7: Run the Chatbot with Trimmed Messages
print("\n🤖 Running Chatbot with Message Trimming...")
output = graph.invoke({'messages': trimmed_messages})

# Step 8: Append AI Response and Ask Follow-Up Question
messages.append(output['messages'][-1])  # Add AI's last response
messages.append(HumanMessage(content="Tell me where Orcas live!", name="Lance"))  # New question

# Step 9: Trim Again Before Sending New Request
messages_out_trim = graph.invoke({'messages': messages})

# Print Final Trimmed Messages
print("\n📝 Chatbot Response After Follow-up Question:")
for m in messages_out_trim["messages"]:
    m.pretty_print()