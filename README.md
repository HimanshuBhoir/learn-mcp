# learn-mcp: Dev Task & Learning Log

A minimal [MCP](https://modelcontextprotocol.io) server built with [FastMCP](https://gofastmcp.com). It lets Claude Code (or any MCP client) manage your dev tasks and log what you learn. It demonstrates the three MCP primitives: tools, resources and prompts.

This is Part 1 (local) of a three-part series. Part 2 hosts it on Render; Part 3 adds auth with Descope. The article is in [content/medium-article.md](content/medium-article.md).

## What it exposes

| Type | Name | What it does |
|---|---|---|
| Tool | `add_task(title, description?)` | Save a new task |
| Tool | `complete_task(task_id)` | Mark a task as done |
| Tool | `delete_task(task_id)` | Delete a task (marked destructive) |
| Tool | `log_learning(topic, notes)` | Record something you learned |
| Resource | `tasks://open` | Open tasks |
| Resource template | `tasks://{task_id}` | One task by ID |
| Resource | `learnings://all` | All learnings |
| Prompt | `plan_my_day(hours?)` | Time-blocked plan from open tasks |
| Prompt | `progress_review()` | Summary of completed tasks and learnings |

Data is stored in `data/db.json`, created on first write. Delete it to start fresh.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone <repo-url>
cd learn-mcp
uv sync
```

## Run

The server uses stdio, so you normally don't start it yourself; the client does. To start it manually:

```bash
uv run server.py
```

## Use with Claude Code

`.mcp.json` already registers the server as `dev-task-log`.

1. Run `claude` in this folder and approve the `dev-task-log` server.
2. Type `/mcp` to check it's connected.
3. Try it:

| Primitive | Example |
|---|---|
| Tool | `Add "Write MCP article" to my Dev Task Log` |
| Resource | `@dev-task-log:tasks://open what should I do next?` |
| Prompt | `/mcp__dev-task-log__plan_my_day 4` |

If Claude uses its built-in todo list instead, mention "Dev Task Log" in your request. After editing `server.py`, reconnect from `/mcp`.

## Use with VS Code

`.vscode/mcp.json` registers the same server. Open this folder in VS Code and start `dev-task-log` from the MCP servers list.

## Test without an AI

```bash
uv run fastmcp list server.py --resources --prompts          # list everything
uv run fastmcp call server.py add_task title="Write article" # call a tool
uv run fastmcp call server.py tasks://open                   # read a resource
uv run fastmcp call server.py plan_my_day hours=3 --prompt   # get a prompt
uv run fastmcp dev inspector server.py                       # browser UI
```

## Project structure

```
learn-mcp/
├── server.py              # the MCP server
├── .mcp.json              # Claude Code config
├── .vscode/mcp.json       # VS Code config
├── data/db.json           # local data (git-ignored)
└── content/               # article drafts
```
