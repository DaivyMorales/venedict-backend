from langgraph.graph import StateGraph, START, END


class State:
    name: str


def node_1(state: State):
    return state


def node_2(state: State):
    return state


builder = StateGraph(State)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)
agent = builder.compile()
