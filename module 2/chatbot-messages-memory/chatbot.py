import os, getpass
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from IPython.display import Image, display

# ✅ Set API keys (for OpenAI & LangChain)
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"

# ✅ Initialize GPT-4o model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# ✅ Define state with messages & summary
class State(MessagesState):
    summary: str

# ✅ Function to call GPT model
def call_model(state: State):
    """Generate a response using OpenAI and include the summary (if exists)."""
    summary = state.get("summary", "")
    messages = state["messages"]

    if summary:
        system_message = SystemMessage(content=f"Summary of conversation: {summary}")
        messages = [system_message] + messages  # Append summary to conversation history
    
    response = model.invoke(messages)
    return {"messages": response}  # Return updated messages

# ✅ Function to summarize conversation
def summarize_conversation(state: State):
    """Create a running summary of the conversation and delete old messages."""
    summary = state.get("summary", "")

    # Create the prompt for summarization
    if summary:
        summary_prompt = f"Current summary: {summary}\n\nExtend the summary with the new messages."
    else:
        summary_prompt = "Summarize the conversation."

    # Append summary request to chat history
    messages = state["messages"] + [HumanMessage(content=summary_prompt)]
    response = model.invoke(messages)

    # Keep only the last two messages, remove older ones
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": delete_messages}

# ✅ Function to decide whether to summarize or continue chatting
def should_continue(state: State):
    """Determine next step based on message count."""
    messages = state["messages"]
    return "summarize_conversation" if len(messages) > 6 else END  # Summarize if >6 messages

# ✅ Define the chatbot's conversation graph
workflow = StateGraph(State)

# Add chatbot processing & summarization nodes
workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

# Set conversation flow
workflow.add_edge(START, "conversation")  # Start with conversation
workflow.add_conditional_edges("conversation", should_continue)  # Check when to summarize
workflow.add_edge("summarize_conversation", END)  # End after summarization

# ✅ Enable memory persistence
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# ✅ Display conversation flowchart
display(Image(graph.get_graph().draw_mermaid_png()))
