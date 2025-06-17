import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for the MCP server, sourced from environment variables."""

    mcp_server_port: str | None = os.getenv("MCP_SERVER_PORT")
    fastmcp_port: str | None = os.getenv("FASTMCP_PORT")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    fastmcp_host: str = os.getenv("FASTMCP_HOST", "0.0.0.0")