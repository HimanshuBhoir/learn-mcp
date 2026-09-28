# Project Architecture

This project is a local MCP server built with Python and FastMCP.

## Components

- server.py → MCP server entry point
- data/ → project information exposed as MCP resources
- Tools → actions Claude can execute
- Resources → information Claude can read
- Prompts → reusable instructions

## Flow

Claude Code
    ↓
MCP Client
    ↓
FastMCP Server
    ├── Tools
    ├── Resources
    └── Prompts