import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated

import operator

# ✅ Set API Keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("TAVILY_API_KEY")

# ✅ Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ✅ Define State Structure
class State(TypedDict):
    question: str
    answer: str
    context: Annotated[list, operator.add]  # Combines context from multiple sources

# ✅ Wikipedia Search Function
def search_wikipedia(state):
    """ Retrieve documents from Wikipedia """
    search_docs = WikipediaLoader(query=state['question'], load_max_docs=2).load()
    
    # Format Wikipedia context
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}">\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

# ✅ Web Search Function
def search_web(state):
    """ Retrieve documents from a web search """
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(state['question'])

    # Format Web search context
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

# ✅ LLM Answer Generation
def generate_answer(state):
    """ Generate answer using LLM """
    context = state["context"]
    question = state["question"]

    # Template for structured answering
    answer_template = """Answer the question "{question}" using this context: {context}"""
    answer_instructions = answer_template.format(question=question, context=context)

    # Invoke LLM
    answer = llm.invoke([SystemMessage(content=answer_instructions)] + [HumanMessage(content="Answer the question.")])

    return {"answer": answer}

# ✅ Create Graph
builder = StateGraph(State)

# Add nodes for Wikipedia, Web search, and answer generation
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("search_web", search_web)
builder.add_node("generate_answer", generate_answer)

# Define execution flow
builder.add_edge(START, "search_wikipedia")  # Start → Wikipedia
builder.add_edge(START, "search_web")        # Start → Web Search
builder.add_edge("search_wikipedia", "generate_answer")  # Wikipedia → Answer
builder.add_edge("search_web", "generate_answer")        # Web Search → Answer
builder.add_edge("generate_answer", END)  # Answer → End

# ✅ Compile Graph
graph = builder.compile()

# ✅ Visualize Graph
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))

# ✅ Run the Graph with a Question
result = graph.invoke({"question": "How were Nvidia's Q2 2024 earnings?"})

# ✅ Output Answer
print(result['answer'].content)
