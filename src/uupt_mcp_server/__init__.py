# __init__.py
from .order import mcp

def main():
    """MCP UUPT OpenAPI Server - HTTP call UUPT OpenAPI API for MCP."""
    mcp.run()

if __name__ == "__main__":
    main()