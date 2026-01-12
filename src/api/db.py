import os
import psycopg
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from fastapi import FastAPI, Depends
from typing import Annotated

DB_URI = os.getenv("DB_URL")

_checkpointer: AsyncPostgresSaver | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _checkpointer

    global _checkpointer
    # We use psycopg.AsyncConnection.connect directly to have full control over connection parameters
    # This helps avoid 'prepared statement already exists' errors in pooled environments like Supabase
    async with await psycopg.AsyncConnection.connect(
        DB_URI, autocommit=True, prepare_threshold=None, row_factory=dict_row
    ) as conn:
        _checkpointer = AsyncPostgresSaver(conn)
        await _checkpointer.setup()
        yield


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError(
            "Checkpointer not initialized. Make sure lifespan is running"
        )
    return _checkpointer


CheckpointerDep = Annotated[AsyncPostgresSaver, Depends(get_checkpointer)]
