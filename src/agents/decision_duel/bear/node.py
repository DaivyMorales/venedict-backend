from agents.decision_duel.state import State
from langchain_openai import ChatOpenAI
from agents.decision_duel.bear.tools import tools
from agents.decision_duel.bear.prompt import prompt_template
from langgraph.prebuilt import create_react_agent
from datetime import datetime


def bear(state: State):
    asset = state.get("asset")

    llm = ChatOpenAI(model="gpt-4.1-mini")

    system_message = prompt_template.format(
        asset=asset,
        date=datetime.now().strftime("%d/%m/%Y"),
    )

    agent = create_react_agent(llm, tools, prompt=system_message)

    response_bull = state.get("response_bull")
    if response_bull:
        prompt = f"El agente Bull ha presentado el siguiente argumento: {response_bull}. Refuta su argumento haciendo citas de lo que dijo y respondiendo."
    else:
        prompt = "Genera tu argumento inicial Bear."

    messages = state.get("messages", []) + [("user", prompt)]
    result = agent.invoke({"messages": messages})

    last_message = result["messages"][-1]

    return {
        "response_bear": last_message.content,
        "messages": [last_message],
        "debate_turns": state.get("debate_turns", 0) + 1,
    }
