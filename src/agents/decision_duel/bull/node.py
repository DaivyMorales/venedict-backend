from agents.decision_duel.state import State, split_into_bubbles
from langchain_openai import ChatOpenAI
from agents.decision_duel.bull.tools import tools
from agents.decision_duel.bull.prompt import prompt_template
from langgraph.prebuilt import create_react_agent
from datetime import datetime


def bull(state: State):
    asset = state.get("asset")

    llm = ChatOpenAI(model="gpt-4.1-mini")
    term = state.get("term")
    language = state.get("language")

    system_message = prompt_template.format(
        asset=asset,
        date=datetime.now().strftime("%d/%m/%Y"),
        term=term,
        language=language,
    )

    agent = create_react_agent(llm, tools, prompt=system_message)

    response_bear = state.get("response_bear")
    if response_bear:
        prompt = f"El agente Bear ha presentado el siguiente argumento: {response_bear}. Genera tu contra-argumento Bull. Refuta su argumento haciendo citas de lo que dijo y respondiendo."
    else:
        prompt = "Genera tu argumento inicial Bull."

    messages = state.get("messages", []) + [("user", prompt)]
    result = agent.invoke({"messages": messages})

    last_message = result["messages"][-1]

    return {
        "response_bull": last_message.content,
        "bull_bubbles": split_into_bubbles(last_message.content),
        "messages": [last_message],
    }
