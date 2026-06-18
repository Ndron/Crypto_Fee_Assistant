import asyncio
import json
import logging
import os
import threading
import time
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

try:
    from mcp.client.streamable_http import streamablehttp_client
    HAS_STREAMABLE = True
except ImportError:
    HAS_STREAMABLE = False

logger = logging.getLogger(__name__)

SERVER_PREFIX = "srv__"
SEPARATOR = "__"

_servers_cache: dict[str, Any] = {}
_cache_lock = threading.Lock()
_cache_ttl = 300

_in_docker = os.path.exists("/.dockerenv")


def resolve_mcp_url(url: str) -> str:
    if _in_docker:
        url = url.replace("localhost", "host.docker.internal")
        url = url.replace("127.0.0.1", "host.docker.internal")
    return url


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        result = [None, None]
        def _thread_target():
            new_loop = asyncio.new_event_loop()
            try:
                result[0] = new_loop.run_until_complete(coro)
            except Exception as e:
                result[1] = e
            finally:
                new_loop.close()
        t = threading.Thread(target=_thread_target)
        t.start()
        t.join(timeout=30)
        if result[1]:
            raise result[1]
        return result[0]
    else:
        return asyncio.run(coro)


async def _list_tools_sse(url: str) -> list[dict]:
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return mcp_tools_to_openai_format(tools_result.tools)


async def _list_tools_streamable(url: str) -> list[dict]:
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return mcp_tools_to_openai_format(tools_result.tools)


def list_tools_sync(url: str) -> list[dict]:
    resolved_url = resolve_mcp_url(url)
    try:
        return _run_async(_list_tools_sse(resolved_url))
    except Exception:
        pass
    if HAS_STREAMABLE:
        try:
            return _run_async(_list_tools_streamable(resolved_url))
        except Exception:
            pass
    logger.warning(f"Failed to connect to MCP server at {resolved_url}")
    return []


def get_tools_cached(url: str) -> list[dict]:
    now = time.time()
    with _cache_lock:
        if url in _servers_cache:
            tools, ts = _servers_cache[url]
            if now - ts < _cache_ttl:
                return tools
    tools = list_tools_sync(url)
    with _cache_lock:
        _servers_cache[url] = (tools, now)
    return tools


async def _call_tool_sse(url: str, tool_name: str, arguments: dict) -> str:
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return _extract_text(result)


async def _call_tool_streamable(url: str, tool_name: str, arguments: dict) -> str:
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return _extract_text(result)


def _extract_text(result) -> str:
    texts = []
    for content in result.content:
        if hasattr(content, "text"):
            texts.append(content.text)
        elif hasattr(content, "data"):
            texts.append(str(content.data))
    return "\n".join(texts) if texts else str(result)


def call_tool_sync(url: str, tool_name: str, arguments: dict) -> str:
    resolved_url = resolve_mcp_url(url)
    try:
        return _run_async(_call_tool_sse(resolved_url, tool_name, arguments))
    except Exception:
        pass
    if HAS_STREAMABLE:
        try:
            return _run_async(_call_tool_streamable(resolved_url, tool_name, arguments))
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return f"Error calling tool {tool_name}: {str(e)}"
    return f"Error calling tool {tool_name}: SSE connection failed"


def mcp_tools_to_openai_format(tools) -> list[dict]:
    openai_tools = []
    for tool in tools:
        schema = tool.inputSchema if hasattr(tool, "inputSchema") else {}
        schema.pop("title", None)
        if "properties" in schema:
            for prop in schema["properties"].values():
                prop.pop("title", None)
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": schema,
            },
        })
    return openai_tools


def get_all_tools(default_url: str, user_servers: list[dict] | None = None) -> list[dict]:
    all_tools = []
    default_tools = get_tools_cached(default_url)
    all_tools.extend(default_tools)

    if user_servers:
        for server in user_servers:
            server_url = server.get("url", "")
            try:
                server_tools = get_tools_cached(server_url)
                prefixed = []
                for tool in server_tools:
                    prefixed_tool = json.loads(json.dumps(tool))
                    original_name = prefixed_tool["function"]["name"]
                    prefixed_name = f"{SERVER_PREFIX}{server['server_id']}{SEPARATOR}{original_name}"
                    prefixed_tool["function"]["name"] = prefixed_name
                    prefixed_tool["function"]["_original_name"] = original_name
                    prefixed_tool["function"]["_server_url"] = server_url
                    prefixed.append(prefixed_tool)
                all_tools.extend(prefixed)
            except Exception as e:
                logger.error(f"Failed to get tools from server {server.get('name')}: {e}")

    return all_tools


def call_user_tool(server_url: str, tool_name: str, arguments: dict) -> str:
    return call_tool_sync(server_url, tool_name, arguments)
