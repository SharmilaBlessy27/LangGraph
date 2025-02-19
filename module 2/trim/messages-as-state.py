import os
import getpass
from pprint import pprint
from IPython.display import Image, display
from langchain_core.messages import AIMessage, HumanMessage
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

# Step 2: Define messages (Conversation State)
messages = [
    AIMessage(content="So you said you were researching ocean mammals?", name="Bot"),
    HumanMessage(content="Yes, I know about whales. But what others should I learn about?", name="Lance"),
]

print("\n📌 Initial Messages:")
for m in messages:
    pprint(m)

# Step 3: Set up OpenAI model
llm = ChatOpenAI(model="gpt-4o")

# Step 4: Define Chat Model Node
def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"])}

# Step 5: Build the Graph using MessagesState
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

# Compile the graph
graph = builder.compile()

# Display the graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Step 6: Run the Chatbot
print("\n🤖 Running Chatbot...")
output = graph.invoke({'messages': messages})

# Step 7: Print Chatbot Response
print("\n📝 Chatbot Response:")
for m in output['messages']:
     m.pretty_print()
