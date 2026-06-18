import logging
import os

from mcp.server.fastmcp import FastMCP

from tools.crypto_tools import register as register_crypto_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("MCP_PORT", "9000"))

mcp = FastMCP(
    name="Crypto Assistant MCP Server",
    host="0.0.0.0",
    port=PORT,
)

register_crypto_tools(mcp)

if __name__ == "__main__":
    logger.info(f"Starting Crypto MCP Server on 0.0.0.0:{PORT}")
    mcp.run(transport="sse")
