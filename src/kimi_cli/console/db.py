"""SQLite database models for Kimijang Console."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

from kimi_cli import logger


class Database:
    """Console database manager."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = project_path
        self.db_path = project_path / ".kimijang" / "console.db"
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Create database and tables if not exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._connect() as conn:
            # Projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    git_remote TEXT,
                    budget REAL DEFAULT 50.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Agents table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    name TEXT NOT NULL,
                    role TEXT CHECK(role IN ('coder', 'reviewer')),
                    model TEXT DEFAULT 'claude-3-5-sonnet',
                    status TEXT CHECK(status IN ('idle', 'working')) DEFAULT 'idle',
                    yolo_mode BOOLEAN DEFAULT 0,
                    max_cost_per_task REAL DEFAULT 10.0,
                    cost_today REAL DEFAULT 0.0,
                    cost_total REAL DEFAULT 0.0,
                    current_task_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    title TEXT NOT NULL,
                    description TEXT,
                    assignee_id TEXT REFERENCES agents(id),
                    status TEXT CHECK(status IN ('todo', 'doing', 'review', 'done')) DEFAULT 'todo',
                    branch TEXT,
                    base_branch TEXT DEFAULT 'main',
                    estimated_cost REAL,
                    actual_cost REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    task_id TEXT REFERENCES tasks(id),
                    agent_id TEXT REFERENCES agents(id),
                    status TEXT CHECK(status IN ('active', 'paused', 'completed')) DEFAULT 'active',
                    cost REAL DEFAULT 0.0,
                    tokens INTEGER DEFAULT 0,
                    branch TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Knowledge notes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    title TEXT NOT NULL,
                    content TEXT,
                    type TEXT CHECK(type IN ('session-summary', 'decision', 'doc')) DEFAULT 'doc',
                    related_task_id TEXT REFERENCES tasks(id),
                    related_session_id TEXT REFERENCES sessions(id),
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Activity log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT REFERENCES projects(id),
                    type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # Project operations
    def get_or_create_project(self, project_id: str) -> dict[str, Any]:
        """Get or create project."""
        with self._connect() as conn:
            # Check if exists
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (project_id,)
            ).fetchone()
            
            if row:
                return dict(row)
            
            # Create new project
            conn.execute(
                "INSERT OR REPLACE INTO projects (id, path) VALUES (?, ?)",
                (project_id, str(self.project_path))
            )
            conn.commit()
            
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (project_id,)
            ).fetchone()
            return dict(row)

    # Agent operations
    def create_agent(self, agent: dict[str, Any]) -> dict[str, Any]:
        """Create new agent."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agents (id, project_id, name, role, model)
                VALUES (?, ?, ?, ?, ?)
            """, (
                agent["id"],
                agent["project_id"],
                agent["name"],
                agent["role"],
                agent.get("model", "claude-3-5-sonnet")
            ))
            conn.commit()
            
            row = conn.execute(
                "SELECT * FROM agents WHERE id = ?",
                (agent["id"],)
            ).fetchone()
            return dict(row)

    def get_agents(self, project_id: str) -> list[dict[str, Any]]:
        """Get all agents for project."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE project_id = ? ORDER BY created_at",
                (project_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def update_agent_status(self, agent_id: str, status: str, task_id: Optional[str] = None) -> None:
        """Update agent status."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE agents SET status = ?, current_task_id = ? WHERE id = ?",
                (status, task_id, agent_id)
            )
            conn.commit()

    # Task operations
    def create_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Create new task."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks (id, project_id, title, description, assignee_id, branch, base_branch, estimated_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task["id"],
                task["project_id"],
                task["title"],
                task.get("description"),
                task.get("assignee_id"),
                task.get("branch"),
                task.get("base_branch", "main"),
                task.get("estimated_cost")
            ))
            conn.commit()
            
            # Log activity
            self._log_activity(conn, task["project_id"], "task_created", 
                f"Task created: {task['title']}", {"task_id": task["id"]})
            
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task["id"],)
            ).fetchone()
            return dict(row)

    def get_tasks(self, project_id: str, status: Optional[str] = None) -> list[dict[str, Any]]:
        """Get tasks for project."""
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project_id = ? AND status = ? ORDER BY created_at",
                    (project_id, status)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at",
                    (project_id,)
                ).fetchall()
            return [dict(row) for row in rows]

    def update_task_status(self, task_id: str, status: str, cost: Optional[float] = None) -> None:
        """Update task status."""
        with self._connect() as conn:
            now = datetime.now().isoformat()
            
            if status == "doing":
                conn.execute(
                    "UPDATE tasks SET status = ?, started_at = ? WHERE id = ?",
                    (status, now, task_id)
                )
            elif status == "done":
                conn.execute(
                    "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                    (status, now, task_id)
                )
            else:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (status, task_id)
                )
            
            if cost is not None:
                conn.execute(
                    "UPDATE tasks SET actual_cost = ? WHERE id = ?",
                    (cost, task_id)
                )
            
            conn.commit()

    # Knowledge operations
    def create_note(self, note: dict[str, Any]) -> dict[str, Any]:
        """Create knowledge note."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notes (id, project_id, title, content, type, related_task_id, related_session_id, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                note["id"],
                note["project_id"],
                note["title"],
                note.get("content", ""),
                note.get("type", "doc"),
                note.get("related_task_id"),
                note.get("related_session_id"),
                note.get("file_path")
            ))
            conn.commit()
            
            row = conn.execute(
                "SELECT * FROM notes WHERE id = ?",
                (note["id"],)
            ).fetchone()
            return dict(row)

    def get_notes(self, project_id: str, note_type: Optional[str] = None) -> list[dict[str, Any]]:
        """Get notes for project."""
        with self._connect() as conn:
            if note_type:
                rows = conn.execute(
                    "SELECT * FROM notes WHERE project_id = ? AND type = ? ORDER BY updated_at DESC",
                    (project_id, note_type)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM notes WHERE project_id = ? ORDER BY updated_at DESC",
                    (project_id,)
                ).fetchall()
            return [dict(row) for row in rows]

    def update_note(self, note_id: str, content: str) -> None:
        """Update note content."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE notes SET content = ?, updated_at = ? WHERE id = ?",
                (content, datetime.now().isoformat(), note_id)
            )
            conn.commit()

    # Dashboard stats
    def get_dashboard_stats(self, project_id: str) -> dict[str, Any]:
        """Get dashboard statistics."""
        with self._connect() as conn:
            # Today's sessions count
            today = datetime.now().strftime("%Y-%m-%d")
            sessions_today = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE project_id = ? AND DATE(created_at) = ?",
                (project_id, today)
            ).fetchone()[0]

            # Tasks done today
            tasks_done = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'done' AND DATE(completed_at) = ?",
                (project_id, today)
            ).fetchone()[0]

            # Total cost
            total_cost = conn.execute(
                "SELECT COALESCE(SUM(actual_cost), 0) FROM tasks WHERE project_id = ?",
                (project_id,)
            ).fetchone()[0]

            # Active agents
            active_agents = conn.execute(
                "SELECT * FROM agents WHERE project_id = ? AND status = 'working'",
                (project_id,)
            ).fetchall()

            # Recent activities
            activities = conn.execute(
                "SELECT * FROM activities WHERE project_id = ? ORDER BY created_at DESC LIMIT 10",
                (project_id,)
            ).fetchall()

            return {
                "sessions_today": sessions_today,
                "tasks_done_today": tasks_done,
                "total_cost": total_cost,
                "active_agents": [dict(row) for row in active_agents],
                "recent_activities": [dict(row) for row in activities]
            }

    def _log_activity(self, conn: sqlite3.Connection, project_id: str, type_: str, message: str, data: Optional[dict] = None) -> None:
        """Log activity."""
        conn.execute(
            "INSERT INTO activities (project_id, type, message, data) VALUES (?, ?, ?, ?)",
            (project_id, type_, message, json.dumps(data) if data else None)
        )
