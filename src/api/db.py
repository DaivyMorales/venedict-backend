import os
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres import PostgresSaver
from fastapi import FastAPI

DB_URI = os.getenv("DB_URI")

_checkpointer: PostgresSaver | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _checkpointer

    global _checkpointer
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        _checkpointer = checkpointer
        _checkpointer.setup()
        yield


def get_checkpointer() -> PostgresSaver:
    if _checkpointer is None:
        raise RuntimeError(
            "Checkpointer not initialized. Make sure lifespan si running"
        )
