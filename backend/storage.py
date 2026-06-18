import json
import os
import logging
from datetime import datetime
from typing import Any
from pathlib import Path

logger = logging.getLogger(__name__)

class JsonStorage:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, filename: str) -> Path:
        return self.data_dir / filename

    def load(self, filename: str, default: Any = None) -> Any:
        path = self._path(filename)
        if not path.exists():
            return default if default is not None else {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load {filename}: {e}")
            return default if default is not None else {}

    def save(self, filename: str, data: Any) -> None:
        path = self._path(filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save {filename}: {e}")
            raise


class ConversationStorage:
    def __init__(self, data_dir: str):
        self.storage = JsonStorage(data_dir)
        self.conversations_dir = Path(data_dir) / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)

    def list_conversations(self) -> list[dict]:
        index = self.storage.load("conversations_index.json", [])
        return sorted(index, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_conversation(self, session_id: str) -> dict | None:
        path = self.conversations_dir / f"{session_id}.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_conversation(self, session: dict) -> None:
        session_id = session["id"]
        session["updated_at"] = datetime.now().isoformat()
        path = self.conversations_dir / f"{session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2, default=str)

        index = self.storage.load("conversations_index.json", [])
        existing = next((i for i, s in enumerate(index) if s["id"] == session_id), None)
        entry = {
            "id": session_id,
            "title": session.get("title", "New Chat"),
            "created_at": session.get("created_at", datetime.now().isoformat()),
            "updated_at": session["updated_at"],
        }
        if existing is not None:
            index[existing] = entry
        else:
            index.append(entry)
        self.storage.save("conversations_index.json", index)

    def delete_conversation(self, session_id: str) -> None:
        path = self.conversations_dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
        index = self.storage.load("conversations_index.json", [])
        index = [s for s in index if s["id"] != session_id]
        self.storage.save("conversations_index.json", index)


class ModelsStorage:
    def __init__(self, data_dir: str):
        self.storage = JsonStorage(data_dir)
        self.filename = "models.json"

    def list_models(self) -> list[dict]:
        data = self.storage.load(self.filename, {"models": []})
        return data.get("models", [])

    def add_model(self, model: dict) -> dict:
        models = self.list_models()
        for m in models:
            if m["name"] == model["name"]:
                raise ValueError(f"Model '{model['name']}' already exists")
        models.append(model)
        self.storage.save(self.filename, {"models": models})
        return model

    def delete_model(self, model_id: str) -> None:
        models = self.list_models()
        models = [m for m in models if m["model_id"] != model_id]
        self.storage.save(self.filename, {"models": models})

    def get_model_by_id(self, model_id: str) -> dict | None:
        models = self.list_models()
        return next((m for m in models if m["model_id"] == model_id), None)


class McpServersStorage:
    MAX_SERVERS = 5

    def __init__(self, data_dir: str):
        self.storage = JsonStorage(data_dir)
        self.filename = "mcp_servers.json"

    def list_servers(self) -> list[dict]:
        data = self.storage.load(self.filename, {"servers": []})
        return data.get("servers", [])

    def add_server(self, server: dict) -> dict:
        servers = self.list_servers()
        if len(servers) >= self.MAX_SERVERS:
            raise ValueError(f"Maximum {self.MAX_SERVERS} MCP servers allowed")
        for s in servers:
            if s["name"] == server["name"]:
                raise ValueError(f"Server '{server['name']}' already exists")
        servers.append(server)
        self.storage.save(self.filename, {"servers": servers})
        return server

    def delete_server(self, server_id: str) -> None:
        servers = self.list_servers()
        servers = [s for s in servers if s["server_id"] != server_id]
        self.storage.save(self.filename, {"servers": servers})

    def get_server_by_id(self, server_id: str) -> dict | None:
        servers = self.list_servers()
        return next((s for s in servers if s["server_id"] == server_id), None)
