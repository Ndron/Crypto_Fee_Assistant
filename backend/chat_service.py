import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any

from openai import OpenAI

from config import config, get_openai_client
from mcp_client import (
    SERVER_PREFIX,
    SEPARATOR,
    call_tool_sync,
    call_user_tool,
    get_all_tools,
)
from storage import ConversationStorage

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Crypto Trading Assistant. You help users analyze crypto exchange data.

You have access to MCP tools for:
- Calculating trading fees
- Breakeven price analysis
- Order book imbalance detection
- Funding rate analysis
- Exchange information
- Drawing price charts (candlestick)

IMPORTANT RULES:
- When the user asks to "draw", "show", "display", "plot" a chart or graph of a price — you MUST call the `get_kline_chart` tool.
- When the user asks in Russian like "нарисуй график", "покажи график", "выведи график" — you MUST call the `get_kline_chart` tool.
- Recognize common crypto names: "биткоин" or "bitcoin" = BTCUSDT, "эфириум" or "ethereum" = ETHUSDT, etc.
- For chart requests, choose the appropriate interval: '1h' or '4h' for recent activity, '1d' for longer trends.
- Always explain your calculations clearly.
- Use the tools when users ask about specific crypto data.
- If a tool fails, explain the limitation gracefully and suggest alternatives."""


def _parse_inline_tool_calls(content: str) -> list[dict]:
    tool_calls = []
    func_pattern = re.compile(r"<function=(\w+)>(.*?)</function>", re.DOTALL)
    matches = func_pattern.findall(content)

    for func_name, args_str in matches:
        try:
            args = json.loads(args_str.strip())
        except json.JSONDecodeError:
            param_pattern = re.compile(r"<parameter=(\w+)>(.*?)</parameter>", re.DOTALL)
            params = param_pattern.findall(args_str)
            args = {k: v.strip() for k, v in params}

        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {"name": func_name, "arguments": json.dumps(args)},
        })

    return tool_calls


def resolve_client(model_id: str | None, models_storage) -> tuple[OpenAI, str]:
    if model_id:
        model = models_storage.get_model_by_id(model_id)
        if model:
            client = get_openai_client(
                api_key="ollama",
                base_url=model["endpoint_url"],
            )
            return client, model["name"]

    client = get_openai_client()
    return client, config.model_name


def load_conversation_context(
    session_id: str | None,
    query: str,
    conv_storage: ConversationStorage,
) -> dict:
    if session_id:
        session = conv_storage.get_conversation(session_id)
        if session:
            return session

    now = datetime.now().isoformat()
    title = query[:50] + ("..." if len(query) > 50 else "")
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }


def build_messages(session: dict, current_query: str | None = None) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in session.get("messages", []):
        if msg["role"] in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
        elif msg["role"] == "tool":
            messages.append({
                "role": "tool",
                "content": msg["content"],
                "tool_call_id": msg.get("tool_call_id", ""),
            })
    if current_query:
        messages.append({"role": "user", "content": current_query})
    return messages


def call_model_for_tools(
    client: OpenAI,
    model_name: str,
    messages: list[dict],
    tools: list[dict],
) -> tuple[Any, list[dict]]:
    clean_tools = []
    for tool in tools:
        t = json.loads(json.dumps(tool))
        t["function"].pop("_original_name", None)
        t["function"].pop("_server_url", None)
        clean_tools.append(t)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=clean_tools if clean_tools else None,
            tool_choice="auto" if clean_tools else None,
        )
    except Exception as e:
        logger.error(f"Model call failed: {e}")
        raise

    choice = response.choices[0]
    tool_calls = []

    if choice.message.tool_calls:
        tool_calls = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in choice.message.tool_calls
        ]
    elif choice.message.content:
        inline = _parse_inline_tool_calls(choice.message.content)
        if inline:
            tool_calls = inline

    return choice.message, tool_calls


def execute_tool_calls(
    tool_calls: list[dict],
    default_mcp_url: str,
    user_servers: list[dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    results = []
    charts = []
    for tc in tool_calls:
        func_name = tc["function"]["name"]
        try:
            args = json.loads(tc["function"]["arguments"])
        except json.JSONDecodeError:
            args = {}

        try:
            if func_name.startswith(SERVER_PREFIX):
                parts = func_name.split(SEPARATOR, 1)
                server_id = parts[0][len(SERVER_PREFIX):]
                original_name = parts[1] if len(parts) > 1 else func_name

                server_url = None
                if user_servers:
                    server = next(
                        (s for s in user_servers if s["server_id"] == server_id), None
                    )
                    if server:
                        server_url = server["url"]

                if server_url:
                    result = call_user_tool(server_url, original_name, args)
                else:
                    result = f"Error: Server {server_id} not found"
            else:
                result = call_tool_sync(default_mcp_url, func_name, args)
        except Exception as e:
            result = f"Error executing {func_name}: {str(e)}"

        if func_name == "get_kline_chart":
            try:
                chart_info = json.loads(result) if isinstance(result, str) else result
                if isinstance(chart_info, dict) and "chart_id" in chart_info:
                    charts.append(chart_info)
            except (json.JSONDecodeError, TypeError):
                pass

        results.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": str(result),
        })

    return results, charts


def call_model_final(
    client: OpenAI,
    model_name: str,
    messages: list[dict],
) -> str:
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )
        content = response.choices[0].message.content or ""
        if not content.strip():
            content = "I couldn't generate a response. Please try again."
        return content
    except Exception as e:
        logger.error(f"Final model call failed: {e}")
        return f"Error generating response: {str(e)}"


def save_history_with_tool_calls(
    session: dict,
    user_message: str,
    assistant_message: str,
    tool_calls: list[dict],
    tool_results: list[dict],
    conv_storage: ConversationStorage,
) -> None:
    now = datetime.now().isoformat()
    session["messages"].append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": user_message,
        "timestamp": now,
    })

    for tc in tool_results:
        session["messages"].append({
            "id": str(uuid.uuid4()),
            "role": "tool",
            "content": tc["content"],
            "tool_call_id": tc.get("tool_call_id", ""),
            "timestamp": now,
        })

    session["messages"].append({
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": assistant_message,
        "timestamp": now,
    })

    conv_storage.save_conversation(session)


def build_response(session_id: str, assistant_content: str, token_percent: float = 0, charts: list[dict] | None = None) -> dict:
    result = {
        "session_id": session_id,
        "assistant_message": {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": assistant_content,
            "timestamp": datetime.now().isoformat(),
        },
        "token_percent": token_percent,
    }
    if charts:
        result["charts"] = charts
    return result
