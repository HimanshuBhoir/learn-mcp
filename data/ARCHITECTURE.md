# MCP Server Architecture

## Overview
A FastMCP-based local development server that demonstrates MCP primitives including tools, resources, and prompts. Built as a learning project to understand Model Context Protocol capabilities.

## Project Structure
```
learn-mcp/
├── server.py              # Main MCP server implementation
├── pyproject.toml         # Project metadata and dependencies
├── .python-version        # Python version specification
├── .vscode/mcp.json      # VS Code MCP configuration
├── README.md             # Project documentation
├── data/
│   ├── ARCHITECTURE.md   # Architecture documentation (this file)
│   └── project.md        # Project details
├── src/
│   └── learn_mcp/
│       └── __init__.py   # Package initialization
└── uv.lock               # Dependency lock file
```

## Core Components

### 1. MCP Server Instance
- **File**: `server.py`
- **Framework**: FastMCP (Python MCP implementation)
- **Initialization**: `FastMCP("Local Development Server")`

### 2. Tools
#### create_task(title: str, description: str) -> str
- **Purpose**: Creates a task with title and description
- **Type**: MCP Tool
- **Decorator**: `@mcp.tool()`
- **Returns**: Confirmation message with task details

### 3. Resources
#### project://info
- **Purpose**: Exposes project metadata
- **Type**: MCP Resource
- **Decorator**: `@mcp.resource("project://info")`
- **Content**: Project name, language, purpose, environment

#### project://architecture (New)
- **Purpose**: Serves this architecture documentation
- **Type**: MCP Resource
- **Content**: Complete architecture overview

### 4. Prompts
#### code_review(code: str) -> str
- **Purpose**: Generates a code review prompt
- **Type**: MCP Prompt
- **Decorator**: `@mcp.prompt()`
- **Focus Areas**: Correctness, Readability, Error handling, Performance, Security

## Tech Stack
- **Language**: Python 3.12+
- **MCP Framework**: FastMCP >=4.0.10
- **Package Manager**: uv (UV build)
- **Runtime**: Local development server

## How It Works

1. **Server Initialization**: FastMCP instance is created with a friendly name
2. **Endpoint Registration**: Tools, resources, and prompts are registered via decorators
3. **Server Execution**: `mcp.run()` starts the MCP server
4. **Client Communication**: Claude or other MCP clients connect and interact with registered endpoints

## Resource URIs
- `project://info` - Project metadata
- `project://architecture` - Architecture documentation

## Tool Endpoints
- `create_task` - Create task functionality

## Prompt Endpoints
- `code_review` - Code review generation

## Testing & Integration
The server is designed to be tested and integrated within Claude through:
1. Configuration in `.vscode/mcp.json`
2. Direct resource access via `project://` URIs
3. Tool invocation through Claude's tool execution system

## Future Extensibility
- Add database operations
- Implement file I/O operations
- Create data processing pipelines
- Build system integration tools
