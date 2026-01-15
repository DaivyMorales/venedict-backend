from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from langchain_core.messages import HumanMessage

# Load environment variables first
load_dotenv()

# Internal imports after load_dotenv
from api.db import CheckpointerDep, lifespan
from agents.decision_duel.agent import make_graph

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


class Message(BaseModel):
    asset: str
    term: str
    language: str
    message: str | None = None


@app.post("/chat/{chat_id}")
async def chat(chat_id: str, item: Message, checkpointer: CheckpointerDep):
    config = {
        "configurable": {
            "thread_id": chat_id,
        }
    }

    content = item.message or f"Analyze {item.asset}"
    state = {
        "asset": item.asset,
        "term": item.term,
        "language": item.language,
        "messages": [HumanMessage(content=content)],
    }

    agent = make_graph(config={"checkpointer": checkpointer})
    response = await agent.ainvoke(state, config)

    return response


@app.post("/chat/{chat_id}/stream")
async def stream_chat(chat_id: str, item: Message, checkpointer: CheckpointerDep):
    config = {
        "configurable": {
            "thread_id": chat_id,
        }
    }

    content = item.message or f"Analyze {item.asset}"
    human_message = HumanMessage(content=content)

    async def generate_response():
        agent = make_graph(config={"checkpointer": checkpointer})

        state = {
            "asset": item.asset,
            "term": item.term,
            "language": item.language,
            "messages": [human_message],
        }

        async for event in agent.astream(
            state, config, stream_mode=["messages", "updates"]
        ):
            kind, content = event

            if kind == "updates":
                for node_name, update in content.items():
                    if "referee_decision" in update:
                        payload = {
                            "type": "decision",
                            "decision": update["referee_decision"],
                            "sender": node_name,
                        }
                        yield f"data: {json.dumps(payload)}\n\n"

                    elif node_name in ["bull", "bear"]:
                        bubbles = update.get(f"{node_name}_bubbles", [])
                        for bubble in bubbles:
                            payload = {
                                "type": "message",
                                "content": bubble,
                                "sender": node_name,
                            }
                            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")
