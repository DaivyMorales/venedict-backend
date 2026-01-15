from agents.decision_duel.state import State, RefereeDecision
from langchain_openai import ChatOpenAI
from agents.decision_duel.referee.prompt import prompt_template
from datetime import datetime
from langgraph.prebuilt import create_react_agent
from agents.decision_duel.referee.tools import tools


def referee(state: State):
    asset = state.get("asset")
    term = state.get("term")
    language = state.get("language")

    # Usamos gpt-4o-mini (corrección de typo)
    llm = ChatOpenAI(model="gpt-4o-mini")

    # LLM específico para la salida estructurada (sin streaming para evitar tokens de JSON en el stream)
    structured_llm = ChatOpenAI(
        model="gpt-4o-mini", streaming=False
    ).with_structured_output(RefereeDecision)

    system_message = prompt_template.format(
        asset=asset,
        date=datetime.now().strftime("%d/%m/%Y"),
        messages=state.get("messages", []),
        language=language,
        term=term,
    )

    agent = create_react_agent(llm, tools, prompt=system_message)

    # Ejecutamos el agente (este sí puede streamear su razonamiento)
    result = agent.invoke(
        {
            "messages": [
                ("user", "Evaluate the debate and issue your structured verdict.")
            ]
        }
    )

    # El veredicto final se obtiene de forma silenciosa
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
