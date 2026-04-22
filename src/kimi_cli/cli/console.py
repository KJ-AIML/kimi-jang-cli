"""Console command for Kimijang Console."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

cli = typer.Typer(help="Run Kimijang Console dashboard.")


@cli.callback(invoke_without_command=True)
def console(
    ctx: typer.Context,
    path: Annotated[
        Path,
        typer.Option("--path", "-p", help="Project path"),
    ] = Path.cwd(),
    port: Annotated[
        int,
        typer.Option("--port", help="Port to bind to"),
    ] = 8080,
    host: Annotated[
        str,
        typer.Option("--host", help="Host to bind to"),
    ] = "127.0.0.1",
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open browser automatically"),
    ] = True,
):
    """Run Kimijang Console dashboard for current project."""
    from kimi_cli.console.cli import start
    
    start(path=path, port=port, host=host, open_browser=open_browser)


@cli.command()
def init(
    path: Annotated[
        Path,
        typer.Option("--path", "-p", help="Project path"),
    ] = Path.cwd(),
) -> None:
    """Initialize console for current project."""
    from kimi_cli.console.cli import init as init_console
    
    init_console(path=path)
