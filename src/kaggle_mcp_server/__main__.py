#!/usr/bin/env python3
"""
Main entry point for running the Kaggle MCP Server as a module.
"""

if __name__ == "__main__":
    from .server import mcp
    mcp.run()