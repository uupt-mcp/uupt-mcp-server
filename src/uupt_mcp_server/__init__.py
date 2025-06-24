<<<<<<< HEAD
# __init__.py
=======
>>>>>>> 94ae7af (优化Python兼容性,支持Python3.10)
from .order import mcp

def main():
    """MCP UUPT OpenAPI Server - HTTP call UUPT OpenAPI API for MCP."""
    mcp.run()

if __name__ == "__main__":
    main()