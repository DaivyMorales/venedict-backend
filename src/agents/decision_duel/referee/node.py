from agents.decision_duel.state import State, RefereeDecision
from langchain_openai import ChatOpenAI
from agents.decision_duel.referee.prompt import prompt_template
from datetime import datetime
from langgraph.prebuilt import create_react_agent
from agents.decision_duel.referee.tools import tools


def referee(state: State):
    asset = state.get("asset")

    # Usamos el modelo del entorno del usuario
    llm = ChatOpenAI(model="gpt-4.1-mini")

    system_message = prompt_template.format(
        asset=asset,
        date=datetime.now().strftime("%d/%m/%Y"),
        messages=state.get("messages", []),
    )

    # Cambiamos state_modifier por prompt para compatibilidad
    agent = create_react_agent(llm, tools, prompt=system_message)

    # Ejecutamos el agente
    result = agent.invoke(
        {
            "messages": [
                ("user", "Evaluate the debate and issue your structured verdict.")
            ]
        }
    )

    # Para obtener la salida estructurada final, usamos una segunda llamada o pedimos al agente que formatee.
    # Una forma limpia es invocar el LLM con structured_output usando el resultado del proceso anterior.
    structured_llm = llm.with_structured_output(RefereeDecision)
    final_verdict = structured_llm.invoke(
        [
            ("system", system_message),
            (
                "user",
                f"Based on the following analysis, provide the final structured decision: {result['messages'][-1].content}",
            ),
        ]
    )

    return {
        "referee_decision": final_verdict,
        "messages": [
            (
                "ai",
                f"Verdict: {final_verdict['winner']} wins. {final_verdict['reason']}",
            )
        ],
    }
