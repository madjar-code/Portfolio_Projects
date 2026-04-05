import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from consumer import start_consumer

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_consumer())
    yield
    task.cancel()


app = FastAPI(title="Bureaucratic AI Agent", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
