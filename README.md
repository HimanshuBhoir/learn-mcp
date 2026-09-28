# learn-mcp: Dev Task & Learning Log

A minimal [MCP](https://modelcontextprotocol.io) server built with [FastMCP](https://gofastmcp.com). It lets Claude Code (or any MCP client) manage your dev tasks and log what you learn. It demonstrates the three MCP primitives: tools, resources and prompts.

Part of a three-part series:

1. **Local**: run it over stdio with Claude Code. Article: [content/medium-article.md](content/medium-article.md).
2. **Hosted**: deploy it to Render over HTTP (below). Article: [content/medium-article-part2.md](content/medium-article-part2.md).
3. **Secured**: add auth with Descope (coming next).

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

Data is stored in `data/db.json`, created on first write. Delete it to start fresh. On Render this file is temporary (see [Deploy to Render](#deploy-to-render)).

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

To run it as a web server (same as Render), serving MCP at `http://127.0.0.1:8000/mcp`:

```bash
uv run fastmcp run server.py --transport http --port 8000
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

## Deploy to Render

Create a **Web Service** from this repo (Python runtime) with:

| Setting | Value |
|---|---|
| Branch | The branch you want to deploy, e.g. `release/phase1` |
| Build Command | `uv sync --frozen && uv cache prune --ci` |
| Start Command | `uv run fastmcp run server.py --transport http --host 0.0.0.0 --port $PORT` |

No code changes are needed; the start command switches the transport to HTTP. The server is then available at `https://<your-service>.onrender.com/mcp`. Opening that URL in a browser shows an error, which is expected: MCP clients send POST requests.

Test it:

```bash
uv run fastmcp call https://<your-service>.onrender.com/mcp add_task title="Hello from Render" --auth none
uv run fastmcp call https://<your-service>.onrender.com/mcp tasks://open --auth none
```

Connect Claude Code to it:

```bash
claude mcp add --transport http dev-task-log-remote https://<your-service>.onrender.com/mcp
```

Things to know:

- **Data is temporary.** `db.json` lives on Render's temporary disk, at `/opt/render/project/src/data/db.json`. It is wiped on every redeploy, restart or spin-down. Use a persistent disk (paid plans) or a hosted database to keep it.
- **Cold starts.** Free services sleep when idle, so the first request after a break can be slow.
- **No auth yet.** Anyone with the URL can read and change tasks. Keep the URL private until Part 3.

## Project structure

```
learn-mcp/
├── server.py              # the MCP server
├── .mcp.json              # Claude Code config
├── .vscode/mcp.json       # VS Code config
├── data/db.json           # data file (git-ignored, created on first write)
└── content/               # article drafts
```
