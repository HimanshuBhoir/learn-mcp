import json
from datetime import date
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP(
    "Dev Task & Learning Log",
    instructions="The user's persistent task and learning log. When the user asks to add, "
    "complete, delete or list their tasks, use these tools, not a built-in todo list.",
)
DB_FILE = Path(__file__).parent / "data" / "db.json"


def load() -> dict:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return {"tasks": [], "learnings": []}


def save(db: dict) -> None:
    DB_FILE.parent.mkdir(exist_ok=True)
    DB_FILE.write_text(json.dumps(db, indent=2), encoding="utf-8")


def find_task(db: dict, task_id: int) -> dict:
    for task in db["tasks"]:
        if task["id"] == task_id:
            return task
    raise ToolError(f"Task {task_id} not found.")


# ---------- Tools: actions the model can take ----------

@mcp.tool()
def add_task(title: str, description: str = "") -> dict:
    """Save a new task to the user's persistent Dev Task Log (survives restarts)."""
    db = load()
    new_id = max((t["id"] for t in db["tasks"]), default=0) + 1
    task = {"id": new_id, "title": title, "description": description, "done": False}
    db["tasks"].append(task)
    save(db)
    return task


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark a task in the user's Dev Task Log as done."""
    db = load()
    task = find_task(db, task_id)
    task["done"] = True
    save(db)
    return task


@mcp.tool(annotations={"destructiveHint": True})
def delete_task(task_id: int) -> str:
    """Permanently delete a task from the user's Dev Task Log."""
    db = load()
    db["tasks"].remove(find_task(db, task_id))
    save(db)
    return f"Task {task_id} deleted."


@mcp.tool()
def log_learning(topic: str, notes: str) -> dict:
    """Record something the user learned today."""
    db = load()
    entry = {"topic": topic, "notes": notes, "date": date.today().isoformat()}
    db["learnings"].append(entry)
    save(db)
    return entry


# ---------- Resources: read-only data ----------

@mcp.resource("tasks://open")
def open_tasks() -> str:
    """All open tasks."""
    return json.dumps([t for t in load()["tasks"] if not t["done"]], indent=2)


@mcp.resource("tasks://{task_id}")
def task_detail(task_id: int) -> str:
    """A single task by ID."""
    return json.dumps(find_task(load(), task_id), indent=2)


@mcp.resource("learnings://all")
def all_learnings() -> str:
    """Everything the user has logged as learned."""
    return json.dumps(load()["learnings"], indent=2)


# ---------- Prompts: reusable templates ----------

@mcp.prompt()
def plan_my_day(hours: int = 8) -> str:
    """Plan today using the open tasks."""
    return f"I have {hours} hours today. Build a time-blocked plan from my open tasks:\n{open_tasks()}"


@mcp.prompt()
def progress_review() -> str:
    """Summarise completed tasks and learnings."""
    db = load()
    done = [t for t in db["tasks"] if t["done"]]
    return (
        "Summarise my progress and suggest what to focus on next.\n"
        f"Completed tasks:\n{json.dumps(done, indent=2)}\n"
        f"Learnings:\n{json.dumps(db['learnings'], indent=2)}"
    )


if __name__ == "__main__":
    mcp.run()
