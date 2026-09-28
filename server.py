import json
import os
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError, ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

import storage

mcp = FastMCP(
    "Dev Task & Learning Log",
    instructions="Tracks the user's dev tasks and daily learnings. "
    "Use the tools to change data and the resources to read it.",
)

# Phase 3 replaces this with the authenticated user's ID from the access token.
USER_ID = "local"

storage.init_db()


# ---------- Tools: actions the model can take ----------

@mcp.tool()
def add_task(
    title: Annotated[str, Field(description="Short task title, e.g. 'Fix login bug'")],
    description: Annotated[str, Field(description="Optional details about the task")] = "",
) -> dict:
    """Add a new open task to the user's task list."""
    return storage.add_task(USER_ID, title, description)


@mcp.tool(annotations=ToolAnnotations(idempotent_hint=True))
def complete_task(
    task_id: Annotated[int, Field(description="ID of the task to mark as done")],
) -> dict:
    """Mark an open task as done."""
    task = storage.complete_task(USER_ID, task_id)
    if task is None:
        raise ToolError(f"Task {task_id} not found.")
    return task


@mcp.tool(annotations=ToolAnnotations(destructive_hint=True))
def delete_task(
    task_id: Annotated[int, Field(description="ID of the task to delete permanently")],
) -> str:
    """Permanently delete a task. This cannot be undone."""
    if not storage.delete_task(USER_ID, task_id):
        raise ToolError(f"Task {task_id} not found.")
    return f"Task {task_id} deleted."


@mcp.tool()
def log_learning(
    topic: Annotated[str, Field(description="What the learning is about, e.g. 'MCP resources'")],
    notes: Annotated[str, Field(description="What was learned, in the user's own words")],
) -> dict:
    """Record something the user learned today."""
    return storage.add_learning(USER_ID, topic, notes)


# ---------- Resources: read-only data the client can load ----------

@mcp.resource("tasks://open", mime_type="application/json")
def open_tasks() -> str:
    """All open tasks for the user."""
    return json.dumps(storage.list_tasks(USER_ID, status="open"), indent=2)


@mcp.resource("tasks://{task_id}", mime_type="application/json")
def task_detail(task_id: int) -> str:
    """A single task by ID."""
    task = storage.get_task(USER_ID, task_id)
    if task is None:
        raise ResourceError(f"Task {task_id} not found.")
    return json.dumps(task, indent=2)


@mcp.resource("learnings://recent", mime_type="application/json")
def recent_learnings() -> str:
    """Learnings logged in the last 7 days."""
    return json.dumps(storage.list_learnings(USER_ID, days=7), indent=2)


# ---------- Prompts: reusable templates the user picks ----------

@mcp.prompt()
def plan_my_day(hours_available: int = 8) -> str:
    """Turn the open task list into a realistic plan for today."""
    tasks = storage.list_tasks(USER_ID, status="open")
    return "\n".join([
        f"I have {hours_available} hours of focused time today.",
        "Here are my open tasks as JSON:",
        json.dumps(tasks, indent=2),
        "",
        "Build a time-blocked plan for today. Put the most important tasks first,",
        "estimate how long each takes, and tell me which tasks to postpone.",
    ])


@mcp.prompt()
def weekly_review() -> str:
    """Summarise what was finished and learned over the last 7 days."""
    done = storage.list_completed_since(USER_ID, days=7)
    learned = storage.list_learnings(USER_ID, days=7)
    return "\n".join([
        "Help me write my weekly review.",
        "",
        "Tasks completed this week:",
        json.dumps(done, indent=2),
        "",
        "Things I learned this week:",
        json.dumps(learned, indent=2),
        "",
        "Summarise my progress, group the learnings into themes,",
        "and suggest one thing to focus on next week.",
    ])


def main() -> None:
    if os.getenv("MCP_TRANSPORT", "stdio") == "http":
        mcp.run(
            transport="http",
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
