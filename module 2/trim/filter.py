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

# Step 2: Define Chat Model
llm = ChatOpenAI(model="gpt-4o")

# Step 3: Define Chat Node (Only pass the last message)
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}  # Pass only the last message

# Step 4: Build the Graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

# Compile the graph
graph = builder.compile()

# Display the graph structure
display(Image(graph.get_graph().draw_mermaid_png()))

# Step 5: Create Initial Messages
messages = [
    AIMessage(content="So you said you were researching ocean mammals?", name="Bot"),
    HumanMessage(content="Yes, I know about whales. But what others should I learn about?", name="Lance"),
]

# Step 6: Run the Chatbot with Filtering
print("\n🤖 Running Chatbot with Message Filtering...")
output = graph.invoke({'messages': messages})

# Step 7: Append AI Response and Ask Follow-Up Question
messages.append(output['messages'][-1])  # Add last AI response
messages.append(HumanMessage(content="Tell me more about Narwhals!", name="Lance"))  # New question

# Step 8: Invoke Again Using Message Filtering
print("\n📝 Chatbot Response After Follow-up Question:")
output = graph.invoke({'messages': messages})

# Print Final Messages
for m in output['messages']:
    m.pretty_print()
