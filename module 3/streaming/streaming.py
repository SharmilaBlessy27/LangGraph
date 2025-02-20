import os, getpass
from IPython.display import Image, display

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState


# Function to set environment variables
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("OPENAI_API_KEY")


# Define the model
model = ChatOpenAI(model="gpt-4o", temperature=0)


# Define chatbot state
class State(MessagesState):
    summary: str


# Function to call the model and handle memory
def call_model(state: State, config: RunnableConfig):
    summary = state.get("summary", "")

    # Add summary to system message if it exists
    messages = state["messages"]
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + messages

    response = model.invoke(messages, config)
    return {"messages": response}


# Function to summarize conversation when needed
def summarize_conversation(state: State):
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Keep only the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": delete_messages}


# Function to decide whether to continue or summarize
def should_continue(state: State):
    messages = state["messages"]

    # Summarize if more than 6 messages
    if len(messages) > 6:
        return "summarize_conversation"
    return END


# Build the graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile the graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Display graph structure
display(Image(graph.get_graph().draw_mermaid_png()))


# **Streaming Conversation State Updates**
print("\n### Streaming with 'updates' mode ###")
config = {"configurable": {"thread_id": "1"}}
for chunk in graph.stream({"messages": [HumanMessage(content="hi! I'm Lance")]}, config, stream_mode="updates"):
    print(chunk)


# **Streaming Full Graph State**
print("\n### Streaming with 'values' mode ###")
config = {"configurable": {"thread_id": "2"}}
input_message = HumanMessage(content="hi! I'm Lance")
for event in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    for m in event["messages"]:
        print(m.content)
    print("---" * 25)


# **Streaming Tokens (Real-time)**
import asyncio

async def stream_tokens():
    config = {"configurable": {"thread_id": "3"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    
    async for event in graph.astream_events({"messages": [input_message]}, config, version="v2"):
        print(f"Node: {event['metadata'].get('langgraph_node','')}. Type: {event['event']}. Name: {event['name']}")

asyncio.run(stream_tokens())


# **Streaming AI Model Tokens from a Specific Node**
async def stream_specific_node():
    node_to_stream = "conversation"
    config = {"configurable": {"thread_id": "4"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    
    async for event in graph.astream_events({"messages": [input_message]}, config, version="v2"):
        if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node", "") == node_to_stream:
            print(event["data"])

asyncio.run(stream_specific_node())


# **Streaming AI Tokens as they Arrive**
async def stream_tokens_live():
    node_to_stream = "conversation"
    config = {"configurable": {"thread_id": "5"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    
    async for event in graph.astream_events({"messages": [input_message]}, config, version="v2"):
        if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node", "") == node_to_stream:
            data = event["data"]
            print(data["chunk"].content, end="|")

asyncio.run(stream_tokens_live())
