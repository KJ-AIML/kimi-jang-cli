"""CLI command for Kimijang Console."""

from __future__ import annotations

import os
import signal
import sys
import webbrowser
from pathlib import Path
from threading import Thread
from time import sleep

import typer
import uvicorn

from kimi_cli import logger
from kimi_cli.console.app import create_console_app

console_cli = typer.Typer(help="Kimijang Console - Project dashboard")


def _detect_git_remote(project_path: Path) -> str | None:
    """Detect git remote URL."""
    git_config = project_path / ".git" / "config"
    if not git_config.exists():
        return None
    
    try:
        content = git_config.read_text()
        for line in content.split("\n"):
            if "url = " in line:
                return line.split("url = ")[1].strip()
    except Exception:
        pass
    return None


def _get_project_id(project_path: Path) -> str:
    """Generate project ID from path."""
    # Use folder name + parent hash
    folder_name = project_path.name
    parent_hash = str(hash(str(project_path.parent)))[-6:]
    return f"{folder_name}-{parent_hash}"


@console_cli.command()
def init(
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Project path"),
) -> None:
    """Initialize console for current project."""
    project_id = _get_project_id(path)
    
    # Create .kimijang directory
    kimijang_dir = path / ".kimijang"
    kimijang_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (kimijang_dir / "knowledge").mkdir(exist_ok=True)
    (kimijang_dir / "agents").mkdir(exist_ok=True)
    
    # Create config file
    config_file = kimijang_dir / "config.toml"
    if not config_file.exists():
        git_remote = _detect_git_remote(path)
        
        config_content = f'''# Kimijang Console Configuration
project_id = "{project_id}"
name = "{path.name}"
git_remote = "{git_remote or ''}"
budget = 50.00
auto_commit = true

[agents]
default_model = "claude-3-5-sonnet"
max_agents = 5

[features]
auto_summarize = true
knowledge_sync = true
'''
        config_file.write_text(config_content)
    
    # Initialize database (will be created on first run)
    from kimi_cli.console.db import Database
    db = Database(path)
    db.get_or_create_project(project_id)
    
    typer.echo(f"✅ Console initialized for project: {path.name}")
    typer.echo(f"   Project ID: {project_id}")
    typer.echo(f"   Config: {config_file}")
    if git_remote:
        typer.echo(f"   Git remote: {git_remote}")
    typer.echo(f"\nRun 'kimijang console' to start the dashboard.")


@console_cli.command()
def start(
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Project path"),
    port: int = typer.Option(8080, "--port", help="Server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="Server host"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically"),
) -> None:
    """Start console for current project."""
    kimijang_dir = path / ".kimijang"
    
    # Auto-init if not exists
    if not kimijang_dir.exists():
        typer.echo("Initializing console...")
        init(path=path)
    
    project_id = _get_project_id(path)
    
    # Create FastAPI app
    app = create_console_app(path, project_id)
    
    # Banner
    typer.echo(f"\n🟣 Kimijang Console")
    typer.echo(f"   Project: {path.name}")
    typer.echo(f"   URL: http://{host}:{port}")
    typer.echo(f"\n   Press Ctrl+C to stop\n")
    
    # Open browser in background thread
    if open_browser:
        def open_browser_delayed():
            sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")
        
        Thread(target=open_browser_delayed, daemon=True).start()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        typer.echo("\n\n👋 Stopping console...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False
        )
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Console stopped.")


# Alias: console = start
@console_cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    path: Path = typer.Option(Path.cwd(), "--path", "-p"),
    port: int = typer.Option(8080, "--port"),
    host: str = typer.Option("127.0.0.1", "--host"),
    open_browser: bool = typer.Option(True, "--open/--no-open"),
) -> None:
    """Start Kimijang Console (default command)."""
    if ctx.invoked_subcommand is None:
        start(path=path, port=port, host=host, open_browser=open_browser)
