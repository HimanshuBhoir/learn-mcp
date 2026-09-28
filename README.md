# learn-mcp: Dev Task & Learning Log

A minimal [MCP](https://modelcontextprotocol.io) server built with [FastMCP](https://gofastmcp.com). It lets Claude Code (or any MCP client) manage your dev tasks and log what you learn. It demonstrates the three MCP primitives: tools, resources and prompts.

Part of a three-part series:

1. **Local**: run it over stdio with Claude Code. Article: [content/medium-article.md](content/medium-article.md).
2. **Hosted**: deploy it to Render over HTTP (below). Article: [content/medium-article-part2.md](content/medium-article-part2.md).
3. **Secured**: require login with Descope and give each user their own data (below). Article: [content/medium-article-part3.md](content/medium-article-part3.md).

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

Data is stored in `data/db.json`, created on first write, and grouped by user: each logged-in user sees only their own tasks and learnings. Without login (local stdio), everything belongs to the user `local`. Delete the file to start fresh. On Render this file is temporary (see [Deploy to Render](#deploy-to-render)).

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone <repo-url>
cd learn-mcp
uv sync
```

## Two ways to run it

| | Local (stdio) | Hosted (HTTP on Render) |
|---|---|---|
| Who starts the server | Claude Code / VS Code, on your machine | Render, always on |
| Server address | A command: `uv run server.py` | A URL: `https://learn-mcp-jikq.onrender.com/mcp` |
| Login | None, you are user `local` | Descope login (OAuth) |
| Data | `data/db.json` on your machine | Render's temporary disk, per user |

### Option A: Local (stdio)

**Run it directly.** It waits for MCP messages on stdin, so you'll see nothing happen; press `Ctrl+C` to stop. This is only useful to check it starts:

```bash
uv run server.py
```

**Add it to Claude Code.** Either:

- Run `claude` inside this folder. `.mcp.json` already registers the server as `dev-task-log`; approve it when asked.
- Or register it yourself, so it works from any folder (use the absolute path to this repo):

  ```bash
  claude mcp add dev-task-log -- uv run --directory /absolute/path/to/learn-mcp server.py
  ```

**Add it to VS Code.** Open this folder; `.vscode/mcp.json` already registers `dev-task-log`. Start it from the MCP servers list.

**Test it without an AI:**

```bash
uv run fastmcp list server.py --resources --prompts          # list everything
uv run fastmcp call server.py add_task title="Write article" # call a tool
uv run fastmcp call server.py tasks://open                   # read a resource
uv run fastmcp call server.py plan_my_day hours=3 --prompt   # get a prompt
uv run fastmcp dev inspector server.py                       # browser UI
```

### Option B: Hosted (HTTP)

**Run it.** Render runs it for you with the start command in [Deploy to Render](#deploy-to-render). To run the same HTTP server on your machine (no login), serving `http://127.0.0.1:8000/mcp`:

```bash
uv run fastmcp run server.py --transport http --port 8000
```

**Add it to Claude Code:**

```bash
claude mcp add --transport http dev-task-log-remote https://learn-mcp-jikq.onrender.com/mcp
```

Then run `claude`, type `/mcp`, select `dev-task-log-remote` and choose **Authenticate**. Log in with Descope in the browser that opens.

For the local HTTP server, use `http://127.0.0.1:8000/mcp` instead (no login needed).

**Add it to VS Code.** Add this to `.vscode/mcp.json` under `"servers"`, then start it and sign in when asked:

```json
"dev-task-log-remote": { "type": "http", "url": "https://learn-mcp-jikq.onrender.com/mcp" }
```

**Test it without an AI:**

```bash
uv run fastmcp list https://learn-mcp-jikq.onrender.com/mcp --auth none    # should fail: 401
uv run fastmcp list https://learn-mcp-jikq.onrender.com/mcp --auth oauth   # browser login, then lists tools
uv run fastmcp call https://learn-mcp-jikq.onrender.com/mcp tasks://open --auth oauth
```

### Useful Claude Code commands

```bash
claude mcp list                       # all servers and their status
claude mcp get dev-task-log-remote    # details of one server
claude mcp remove dev-task-log-remote # remove it
```

## Using it in Claude Code

Once connected (either option), try:

| Primitive | Example |
|---|---|
| Tool | `Add "Write MCP article" to my Dev Task Log` |
| Resource | `@dev-task-log:tasks://open what should I do next?` |
| Prompt | `/mcp__dev-task-log__plan_my_day 4` |

For the hosted server, replace `dev-task-log` with `dev-task-log-remote`. If Claude uses its built-in todo list instead, mention "Dev Task Log" in your request. After editing `server.py`, reconnect from `/mcp`.

## Deploy to Render

Create a **Web Service** from this repo (Python runtime) with:

| Setting | Value |
|---|---|
| Branch | The branch you want to deploy, e.g. `main` |
| Build Command | `uv sync --frozen && uv cache prune --ci` |
| Start Command | `uv run fastmcp run server.py --transport http --host 0.0.0.0 --port $PORT` |

The start command switches the transport to HTTP. The server is then available at `https://<your-service>.onrender.com/mcp`. Opening that URL in a browser shows an error, which is expected: MCP clients send POST requests. To connect and test it, follow [Option B](#option-b-hosted-http) with your own URL.

Without the Descope environment variables (see [Authentication](#authentication-descope)), the server is open to anyone.

Things to know:

- **Data is temporary.** `db.json` lives on Render's temporary disk, at `/opt/render/project/src/data/db.json`. It is wiped on every redeploy, restart or spin-down. Use a persistent disk (paid plans) or a hosted database to keep it.
- **Cold starts.** Free services sleep when idle, so the first request after a break can be slow.

## Authentication (Descope)

When `DESCOPE_CONFIG_URL` is set, the server requires a Descope login over HTTP. Local stdio use never asks for login.

### 1. Create the MCP server in Descope

In the Descope Console, go to **Agentic Identity Hub → MCP Servers** and create a server:

| Field | Value |
|---|---|
| Name | `Dev Task & Learning Log` |
| Description | Anything |
| MCP Server URL | `https://<your-service>.onrender.com/mcp` (exact, no trailing slash) |
| Client Registration | Keep **DCR** enabled (default) |
| Scopes | Leave empty |
| User Consent Flow | Default, or **Generate Flow** |

After saving, copy the **Discovery URL (.well-known)** from **Usage Samples**. It looks like:

```
https://api.descope.com/v1/apps/agentic/<ProjectID>/<ServerID>/.well-known/openid-configuration
```

Use this server-level URL, not the project-level one: only the server-level one includes the client registration endpoint that Claude Code and VS Code need.

### 2. Set environment variables on Render

| Key | Value |
|---|---|
| `DESCOPE_CONFIG_URL` | The Discovery URL from step 1 |
| `BASE_URL` | `https://<your-service>.onrender.com` (no `/mcp`, no trailing slash) |

Redeploy after saving. You can keep a copy of these values in `.env` (git-ignored) for reference; local runs don't need it, because the server only turns on login when `DESCOPE_CONFIG_URL` is set in its environment.

### 3. Check it

```bash
# should fail with 401: no token
uv run fastmcp list https://<your-service>.onrender.com/mcp --auth none

# opens the Descope login in your browser, then lists the tools
uv run fastmcp list https://<your-service>.onrender.com/mcp --auth oauth
```

In Claude Code, open `/mcp`, select `dev-task-log-remote`, and choose **Authenticate**. After logging in, use it as before.

**Test auth locally.** Start the HTTP server with Descope turned on (PowerShell shown; in bash use `export`):

```powershell
$env:DESCOPE_CONFIG_URL="<Discovery URL from step 1>"
$env:BASE_URL="http://127.0.0.1:8000"
uv run fastmcp run server.py --transport http --port 8000
```

Then, in a second terminal:

```bash
uv run fastmcp list http://127.0.0.1:8000/mcp --auth none   # fails: 401 Unauthorized
curl http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp   # shows Descope as the login server
```

Close that terminal afterwards, or the variables stay set there. A full browser login against localhost needs a second Descope MCP server whose MCP Server URL is `http://127.0.0.1:8000/mcp`, because Descope issues tokens for the URL it has registered.

**Important:** if `DESCOPE_CONFIG_URL` is missing, the server starts without auth. Run the `--auth none` check after every deploy.

### Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Requested resource not in aud whitelist` | The **MCP Server URL** in Descope is empty or doesn't exactly match the server's URL | Set it to `https://<your-service>.onrender.com/mcp` in the MCP server's settings and save |
| `Received invalid scope ... invalid=[phone]` | The client requested a scope the Descope MCP server doesn't allow | Already handled in `server.py` via `scopes_supported=["openid", "profile", "email"]` |
| `--auth none` still lists the tools | Login is off: `DESCOPE_CONFIG_URL` isn't set where the server runs | Set it on Render (or in the same terminal locally) and restart |
| Claude Code keeps failing after a fix | It kept an earlier failed registration | `claude mcp remove dev-task-log-remote`, add it again, then **Authenticate** |

## Project structure

```
learn-mcp/
├── server.py              # the MCP server
├── .mcp.json              # Claude Code config
├── .vscode/mcp.json       # VS Code config
├── data/db.json           # data file (git-ignored, created on first write)
├── .env                   # copy of the Render settings (git-ignored, optional)
└── content/               # article drafts
```
