import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import MessagesState, END
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

# 🔹 Set API Keys for OpenAI and LangChain
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGCHAIN_API_KEY")

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"

# 🔹 Define Chat Model (GPT-4o)
model = ChatOpenAI(model="gpt-4o", temperature=0)

# 🔹 Define State to Keep Messages & Summary
class State(MessagesState):
    summary: str

# =============================
# 🔹 Function to Call the Model
# =============================
def call_model(state: State):
    """Handles chat messages & adds previous summary if available."""
    
    # Get previous conversation summary (if any)
    summary = state.get("summary", "")

    # If a summary exists, add it to system messages
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    # Generate response using GPT-4o
    response = model.invoke(messages)
    return {"messages": response}

# ==================================
# 🔹 Function to Summarize Messages
# ==================================
def summarize_conversation(state: State):
    """Summarizes conversation when messages exceed 6."""
    
    # Get existing summary (if available)
    summary = state.get("summary", "")

    # Create a prompt for summarization
    if summary:
        summary_message = (
            f"This is a summary of the conversation so far: {summary}\n\n"
            "Extend the summary by including the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    # Append summary prompt to messages
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Keep only the last 2 messages, remove older ones
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": delete_messages}

# =====================================
# 🔹 Function to Decide Next Step
# =====================================
def should_continue(state: State):
    """Decides whether to continue chat or summarize conversation."""
    
    messages = state["messages"]
    
    # If messages exceed 6, summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    
    return END  # Otherwise, end this step

# ==========================
# 🔹 Create Conversation Graph
# ==========================
workflow = StateGraph(State)

# Add nodes
workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

# Define graph flow
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile the graph
memory = MemorySaver()  # Save checkpoints
graph = workflow.compile(checkpointer=memory)

# ==========================
# 🔹 Visualize Conversation Flow
# ==========================
display(Image(graph.get_graph().draw_mermaid_png()))

# ==========================
# 🔹 Start a Conversation (Thread 1)
# ==========================
config = {"configurable": {"thread_id": "1"}}

# 🟢 User starts a chat
input_message = HumanMessage(content="hi! I'm Lance")
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    print(m.pretty_print())

# 🟢 User asks another question
input_message = HumanMessage(content="what's my name?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    print(m.pretty_print())

# 🟢 User talks about sports
input_message = HumanMessage(content="I like the 49ers!")
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    print(m.pretty_print())

# ==========================
# 🔹 Check the Summary (if available)
# ==========================
print("Summary so far:", graph.get_state(config).values.get("summary", ""))

# 🟢 User continues chat later
input_message = HumanMessage(content="I like Nick Bosa, isn't he the highest paid defensive player?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    print(m.pretty_print())

# 🔹 Check Updated Summary
print("Updated Summary:", graph.get_state(config).values.get("summary", ""))
