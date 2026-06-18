import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import config
from chat_service import (
    build_response,
    call_model_final,
    call_model_for_tools,
    execute_tool_calls,
    load_conversation_context,
    resolve_client,
    save_history_with_tool_calls,
    build_messages,
)
from mcp_client import get_all_tools
from storage import ConversationStorage, ModelsStorage, McpServersStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crypto Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = config.data_dir
conv_storage = ConversationStorage(DATA_DIR)
models_storage = ModelsStorage(DATA_DIR)
mcp_servers_storage = McpServersStorage(DATA_DIR)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    model_id: str | None = None


class ModelCreateRequest(BaseModel):
    name: str
    endpoint_url: str
    api_key: str = "ollama"


class McpServerCreateRequest(BaseModel):
    name: str
    url: str
    api_key: str | None = None


def _make_default_model() -> dict:
    return {
        "model_id": "default",
        "name": config.model_name,
        "endpoint_url": config.openai_api_base,
        "is_default": True,
        "created_at": datetime.now().isoformat(),
    }


def _ensure_default_model(models: list[dict]) -> list[dict]:
    if not any(m.get("is_default") for m in models):
        models.insert(0, _make_default_model())
    return models


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        client, model_name = resolve_client(request.model_id, models_storage)
        session = load_conversation_context(request.session_id, request.message, conv_storage)
        messages = build_messages(session, request.message)
        user_servers = mcp_servers_storage.list_servers()
        tools = get_all_tools(config.mcp_server_url, user_servers)

        max_iterations = 5
        all_charts = []
        for _ in range(max_iterations):
            message, tool_calls = call_model_for_tools(client, model_name, messages, tools)

            if not tool_calls:
                assistant_content = message.content or "I couldn't generate a response."
                save_history_with_tool_calls(
                    session, request.message, assistant_content, [], [], conv_storage
                )
                return build_response(session["id"], assistant_content, charts=all_charts or None)

            tool_results, charts = execute_tool_calls(tool_calls, config.mcp_server_url, user_servers)
            all_charts.extend(charts)

            messages.append({"role": "assistant", "content": message.content or "", "tool_calls": tool_calls})
            for tr in tool_results:
                messages.append(tr)

            assistant_content = call_model_final(client, model_name, messages)

            inline_tool_calls = []
            if assistant_content:
                from chat_service import _parse_inline_tool_calls
                inline_tool_calls = _parse_inline_tool_calls(assistant_content)

            if not inline_tool_calls:
                save_history_with_tool_calls(
                    session, request.message, assistant_content, tool_calls, tool_results, conv_storage
                )
                return build_response(session["id"], assistant_content, charts=all_charts or None)

        assistant_content = "I reached the maximum number of tool iterations. Please try a more specific question."
        save_history_with_tool_calls(
            session, request.message, assistant_content, [], [], conv_storage
        )
        return build_response(session["id"], assistant_content, charts=all_charts or None)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations")
async def list_conversations():
    return conv_storage.list_conversations()


@app.get("/api/conversations/{session_id}")
async def get_conversation(session_id: str):
    session = conv_storage.get_conversation(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return session


@app.delete("/api/conversations/{session_id}")
async def delete_conversation(session_id: str):
    conv_storage.delete_conversation(session_id)
    return {"status": "deleted"}


@app.get("/api/models")
async def list_models():
    models = models_storage.list_models()
    return _ensure_default_model(models)


@app.post("/api/models")
async def add_model(request: ModelCreateRequest):
    model = {
        "model_id": str(uuid.uuid4()),
        "name": request.name,
        "endpoint_url": request.endpoint_url,
        "is_default": False,
        "created_at": datetime.now().isoformat(),
    }
    try:
        return models_storage.add_model(model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    if model_id == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default model")
    models_storage.delete_model(model_id)
    return {"status": "deleted"}


@app.get("/api/mcp-servers")
async def list_mcp_servers():
    servers = mcp_servers_storage.list_servers()
    for server in servers:
        try:
            from mcp_client import get_tools_cached
            tools = get_tools_cached(server["url"])
            server["status"] = "online"
            server["tools_count"] = len(tools)
        except Exception:
            server["status"] = "offline"
            server["tools_count"] = 0
    return servers


@app.post("/api/mcp-servers")
async def add_mcp_server(request: McpServerCreateRequest):
    url = request.url.strip()
    if url.endswith("/sse"):
        url = url[:-4]

    server = {
        "server_id": str(uuid.uuid4()),
        "name": request.name,
        "url": url,
        "has_api_key": bool(request.api_key),
        "created_at": datetime.now().isoformat(),
    }
    try:
        result = mcp_servers_storage.add_server(server)
        try:
            from mcp_client import get_tools_cached
            tools = get_tools_cached(url)
            result["status"] = "online"
            result["tools_count"] = len(tools)
        except Exception:
            result["status"] = "offline"
            result["tools_count"] = 0
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/mcp-servers/{server_id}")
async def delete_mcp_server(server_id: str):
    mcp_servers_storage.delete_server(server_id)
    return {"status": "deleted"}


@app.post("/api/mcp-servers/{server_id}/test")
async def test_mcp_server(server_id: str):
    server = mcp_servers_storage.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        from mcp_client import get_tools_cached
        tools = get_tools_cached(server["url"])
        return {"status": "online", "tools_count": len(tools), "tools": [t["function"]["name"] for t in tools]}
    except Exception as e:
        return {"status": "offline", "error": str(e)}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
