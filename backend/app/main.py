"""FastAPI app exposing the LangGraph agent over Server-Sent Events."""
from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.agent import get_agent
from app.config import settings

app = FastAPI(title="Compileit RAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest) -> EventSourceResponse:
    """Stream the agent's response as SSE events.

    Event types emitted:
      - session: { session_id }                    (sent once at start)
      - token:   { text }                          (LLM tokens as they stream)
      - tool:    { name, status, input?, output? } (tool call lifecycle)
      - done:    {}                                (final marker)
      - error:   { message }
    """
    session_id = req.session_id or str(uuid.uuid4())
    agent = get_agent()

    async def event_stream() -> AsyncGenerator[dict, None]:
        yield {"event": "session", "data": json.dumps({"session_id": session_id})}

        config = {"configurable": {"thread_id": session_id}}
        inputs = {"messages": [HumanMessage(content=req.message)]}

        try:
            async for event in agent.astream_events(inputs, config=config, version="v2"):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    text = getattr(chunk, "content", "") or ""
                    if text:
                        yield {"event": "token", "data": json.dumps({"text": text})}

                elif kind == "on_tool_start":
                    yield {
                        "event": "tool",
                        "data": json.dumps(
                            {
                                "name": event["name"],
                                "status": "start",
                                "input": event["data"].get("input"),
                            }
                        ),
                    }

                elif kind == "on_tool_end":
                    output = event["data"].get("output")
                    output_str = str(output)[:500] if output is not None else ""
                    yield {
                        "event": "tool",
                        "data": json.dumps(
                            {"name": event["name"], "status": "end", "output": output_str}
                        ),
                    }
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": json.dumps({"message": str(exc)})}
            return

        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_stream())
