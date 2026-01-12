from dotenv import load_dotenv
from fastapi import FastAPI
from langgraph.checkpoint.postgres import CheckpointerDep

load_dotenv()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello: World"}


class Message:
    text: str


@app.post("/chat/{chat_id}")
async def chat(chat_id: str, item: Message, checkpointer: CheckpointerDep):
    config = {}
