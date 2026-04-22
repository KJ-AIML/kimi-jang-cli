"""FastAPI app for Kimijang Console."""

from __future__ import annotations

import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from kimi_cli import logger
from kimi_cli.console.db import Database


# Global state
console_db: Database | None = None
project_id: str | None = None


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


def get_db() -> Database:
    """Get database instance."""
    if console_db is None:
        raise HTTPException(status_code=500, detail="Console not initialized")
    return console_db


def create_console_app(project_path: Path, proj_id: str) -> FastAPI:
    """Create console FastAPI app."""
    global console_db, project_id
    
    project_id = proj_id
    console_db = Database(project_path)
    
    # Ensure project exists in DB
    console_db.get_or_create_project(proj_id)
    
    # Create default agents if none exist
    _ensure_default_agents(console_db, proj_id)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Console started for project: {proj_id}")
        yield
        logger.info(f"Console stopped for project: {proj_id}")
    
    app = FastAPI(
        title="Kimijang Console",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API Routes
    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "project": proj_id}
    
    # Dashboard
    @app.get("/api/dashboard")
    async def get_dashboard() -> dict[str, Any]:
        db = get_db()
        return db.get_dashboard_stats(proj_id)
    
    # Agents
    @app.get("/api/agents")
    async def list_agents() -> list[dict[str, Any]]:
        db = get_db()
        return db.get_agents(proj_id)
    
    @app.post("/api/agents")
    async def create_agent(agent: dict[str, Any]) -> dict[str, Any]:
        db = get_db()
        agent["id"] = str(uuid.uuid4())[:8]
        agent["project_id"] = proj_id
        
        result = db.create_agent(agent)
        
        # Broadcast update
        await manager.broadcast({
            "type": "agent_created",
            "data": result
        })
        
        return result
    
    @app.patch("/api/agents/{agent_id}/status")
    async def update_agent_status(agent_id: str, update: dict[str, Any]) -> dict[str, str]:
        db = get_db()
        db.update_agent_status(agent_id, update["status"], update.get("task_id"))
        
        await manager.broadcast({
            "type": "agent_updated",
            "data": {"id": agent_id, "status": update["status"]}
        })
        
        return {"status": "ok"}
    
    # Tasks
    @app.get("/api/tasks")
    async def list_tasks(status: str | None = None) -> list[dict[str, Any]]:
        db = get_db()
        return db.get_tasks(proj_id, status)
    
    @app.post("/api/tasks")
    async def create_task(task: dict[str, Any]) -> dict[str, Any]:
        db = get_db()
        task["id"] = str(uuid.uuid4())[:8]
        task["project_id"] = proj_id
        
        # Generate branch name if not provided
        if not task.get("branch"):
            slug = task["title"].lower().replace(" ", "-")[:30]
            task["branch"] = f"feat/{slug}-{task['id'][:4]}"
        
        result = db.create_task(task)
        
        await manager.broadcast({
            "type": "task_created",
            "data": result
        })
        
        return result
    
    @app.patch("/api/tasks/{task_id}/status")
    async def update_task_status(task_id: str, update: dict[str, Any]) -> dict[str, str]:
        db = get_db()
        db.update_task_status(task_id, update["status"], update.get("cost"))
        
        await manager.broadcast({
            "type": "task_updated",
            "data": {"id": task_id, "status": update["status"]}
        })
        
        return {"status": "ok"}
    
    # Knowledge
    @app.get("/api/notes")
    async def list_notes(note_type: str | None = None) -> list[dict[str, Any]]:
        db = get_db()
        return db.get_notes(proj_id, note_type)
    
    @app.post("/api/notes")
    async def create_note(note: dict[str, Any]) -> dict[str, Any]:
        db = get_db()
        note["id"] = str(uuid.uuid4())[:8]
        note["project_id"] = proj_id
        
        result = db.create_note(note)
        
        # Also save to markdown file
        if result.get("file_path"):
            _save_note_to_file(project_path, result)
        
        await manager.broadcast({
            "type": "note_created",
            "data": result
        })
        
        return result
    
    @app.patch("/api/notes/{note_id}")
    async def update_note(note_id: str, update: dict[str, Any]) -> dict[str, str]:
        db = get_db()
        db.update_note(note_id, update["content"])
        
        await manager.broadcast({
            "type": "note_updated",
            "data": {"id": note_id}
        })
        
        return {"status": "ok"}
    
    # WebSocket for real-time updates
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive, handle client messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    # Mount static files (built React app)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    
    return app


def _ensure_default_agents(db: Database, proj_id: str) -> None:
    """Create default agents if none exist."""
    agents = db.get_agents(proj_id)
    if agents:
        return
    
    # Create default coder agent
    db.create_agent({
        "id": "coder-1",
        "project_id": proj_id,
        "name": "Code Writer",
        "role": "coder",
        "model": "claude-3-5-sonnet"
    })
    
    # Create default reviewer agent
    db.create_agent({
        "id": "reviewer-1",
        "project_id": proj_id,
        "name": "Code Reviewer",
        "role": "reviewer",
        "model": "claude-3-5-haiku"
    })


def _save_note_to_file(project_path: Path, note: dict[str, Any]) -> None:
    """Save note to markdown file."""
    try:
        file_path = project_path / ".kimijang" / "knowledge" / note["file_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# {note['title']}

{note.get('content', '')}

---
*Created: {note.get('created_at', '')}*
*Type: {note.get('type', 'doc')}*
"""
        file_path.write_text(content, encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to save note to file: {e}")
