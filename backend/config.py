import os
from openai import OpenAI
import httpx

class Config:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "ollama")
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "http://ollama:11434/v1")
    model_name: str = os.getenv("MODEL_NAME", "llama3.1")
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://mcp-server:9000")
    data_dir: str = os.getenv("DATA_DIR", "/app/data")

_openai_client: OpenAI | None = None

def get_openai_client(
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAI:
    global _openai_client
    if api_key and base_url:
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=httpx.Client(verify=False),
        )
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=Config.openai_api_key,
            base_url=Config.openai_api_base,
            http_client=httpx.Client(verify=False),
        )
    return _openai_client

config = Config()
