from agents.decision_duel.bull.node import bull
from agents.decision_duel.bear.node import bear
from agents.decision_duel.referee.node import referee

from langgraph.graph import StateGraph, START, END
from agents.decision_duel.state import State
from typing import Literal


def should_continue(state: State) -> Literal["bull", "referee"]:
    turns = state.get("debate_turns", 0)
    if turns < 2:
        return "bull"
    return "referee"


builder = StateGraph(State)

builder.add_node("bull", bull)
builder.add_node("bear", bear)
builder.add_node("referee", referee)

builder.add_edge(START, "bull")
builder.add_edge("bull", "bear")
builder.add_conditional_edges("bear", should_continue)
builder.add_edge("referee", END)

agent = builder.compile()
