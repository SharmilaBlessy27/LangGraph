from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
# 🔹 Define input schema (only question)
class InputState(TypedDict):
    question: str

# 🔹 Define output schema (only answer)
class OutputState(TypedDict):
    answer: str

# 🔹 Define overall schema (contains internal notes)
class OverallState(TypedDict):
    question: str
    answer: str
    notes: str  # This will NOT be in the final output

# 🔹 Thinking Node: Uses InputState, adds "answer" and "notes"
def thinking_node(state: InputState) -> OverallState:
    return {"answer": "bye", "notes": "... his name is Lance", "question": state["question"]}

# 🔹 Answer Node: Uses OverallState, but returns only OutputState
def answer_node(state: OverallState) -> OutputState:
    return {"answer": "bye Lance"}

# 🔹 Build the graph with explicit input/output schemas
graph = StateGraph(OverallState, input=InputState, output=OutputState)
graph.add_node("thinking_node", thinking_node)
graph.add_node("answer_node", answer_node)

# 🔹 Define process flow
graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)

# 🔹 Compile and Run the Graph
graph = graph.compile()
result = graph.invoke({"question": "hi"})

# 🔹 Print Output (Filtered)
print("Final Output:", result)
