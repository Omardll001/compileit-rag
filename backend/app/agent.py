"""LangGraph ReAct agent with tool calling and per-session memory."""
from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.prompts import SYSTEM_PROMPT
from app.tools import TOOLS


@lru_cache(maxsize=1)
def get_agent():
    """Build (once) and return the compiled LangGraph agent."""
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
        streaming=True,
    )
    checkpointer = MemorySaver()
    return create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
