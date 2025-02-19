import random
from typing import Literal
from typing_extensions import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ValidationError
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

# Define functions for graph nodes
def node_1(state):
    print("---Node 1---")
    return {"name": state.name + " is ..."}

def node_2(state):
    print("---Node 2---")
    return {"mood": "happy"}

def node_3(state):
    print("---Node 3---")
    return {"mood": "sad"}

def decide_mood(state) -> Literal["node_2", "node_3"]:
    return "node_2" if random.random() < 0.5 else "node_3"


class PydanticState(BaseModel):
    name: str
    mood: str  # "happy" or "sad"

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value):
        if value not in ["happy", "sad"]:
            raise ValueError("Mood must be 'happy' or 'sad'")
        return value

# Test validation
try:
    state = PydanticState(name="Sharmi", mood="sad")  # Invalid mood
except ValidationError as e:
    print("Validation Error:", e)

# Build graph with Pydantic state
builder = StateGraph(PydanticState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile and run the graph
graph = builder.compile()
graph.invoke(PydanticState(name="Lance", mood="happy"))
