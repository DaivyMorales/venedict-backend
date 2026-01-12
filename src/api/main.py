from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from api.db import CheckpointerDep, lifespan
from agents.decision_duel.agent import make_graph
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware

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
    response = agent.invoke(state, config)

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

        # Initial state is important for the referee and other nodes
        state = {
            "asset": item.asset,
            "term": item.term,
            "language": item.language,
            "messages": [human_message],
        }

        async for message_chunk, metadata in agent.astream(
            state, config, stream_mode="messages"
        ):
            if message_chunk.content:
                yield f"data: {message_chunk.content}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")
