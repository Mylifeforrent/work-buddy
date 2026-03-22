"""Work Buddy CLI - Entry point for all agent operations.

Usage:
    workbuddy test --project <name> --type regression
    workbuddy jira create --project <name> --requirement "..."
    workbuddy compliance check --ticket PROJ-1234
    workbuddy release prepare --ticket PROJ-1234
    workbuddy pvt run --project <name>
    workbuddy docs search "query"
    workbuddy alert triage --service <name>
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from work_buddy.core.config import load_app_config, load_project_config, list_projects
from work_buddy.core.container import create_container
from work_buddy.core.logging import setup_logging, get_logger

app = typer.Typer(
    name="workbuddy",
    help="🤖 Work Buddy — Multi-agent SDLC automation system",
    no_args_is_help=True,
)
console = Console()
logger = get_logger(__name__)

# ── Sub-commands ──────────────────────────────────────────────────────────────

test_app = typer.Typer(help="Run browser tests and capture evidence")
jira_app = typer.Typer(help="Jira task management")
compliance_app = typer.Typer(help="ICE compliance validation")
release_app = typer.Typer(help="Release preparation")
pvt_app = typer.Typer(help="PVT health checks")
docs_app = typer.Typer(help="Confluence document retrieval")
alert_app = typer.Typer(help="Production alert triage")

app.add_typer(test_app, name="test")
app.add_typer(jira_app, name="jira")
app.add_typer(compliance_app, name="compliance")
app.add_typer(release_app, name="release")
app.add_typer(pvt_app, name="pvt")
app.add_typer(docs_app, name="docs")
app.add_typer(alert_app, name="alert")


# ── Root commands ─────────────────────────────────────────────────────────────

@app.command()
def status():
    """Show Work Buddy status and configuration."""
    config = load_app_config()
    projects = list_projects()

    console.print(Panel.fit(
        f"[bold cyan]Work Buddy v0.1.0[/bold cyan]\n\n"
        f"Mode: [bold {'green' if config.mode == 'mock' else 'yellow'}]{config.mode}[/bold {'green' if config.mode == 'mock' else 'yellow'}]\n"
        f"Projects: [bold]{len(projects)}[/bold] configured\n"
        f"Log Level: {config.log_level}",
        title="🤖 Status",
        border_style="cyan",
    ))

    if projects:
        console.print("\n[bold]Configured Projects:[/bold]")
        for p in projects:
            proj_config = load_project_config(p)
            icon = "🌐" if proj_config.type == "react-app" else "⚙️"
            console.print(f"  {icon} {proj_config.name} ({proj_config.type})")


# ── Test commands ─────────────────────────────────────────────────────────────

@test_app.command("run")
def test_run(
    project: str = typer.Option(..., "--project", "-p", help="Project name to test"),
    test_type: str = typer.Option("regression", "--type", "-t", help="Test type: regression, smoke, upgrade"),
    baseline: bool = typer.Option(False, "--baseline", help="Capture baseline screenshots for upgrade comparison"),
):
    """Run browser tests and capture evidence for a project."""
    setup_logging()
    logger.info(f"Running {test_type} tests for project: {project}", extra={"agent": "browser-test"})

    config = load_app_config()
    container = create_container(config)

    console.print(f"[bold]Running {test_type} tests for [cyan]{project}[/cyan]...[/bold]")
    # Agent execution will be wired in task group 5
    console.print("[yellow]⚠ Browser Test Agent not yet implemented[/yellow]")


@test_app.command("compare")
def test_compare(
    project: str = typer.Option(..., "--project", "-p", help="Project name"),
):
    """Generate before/after comparison report for upgrades."""
    console.print(f"[bold]Generating upgrade comparison for [cyan]{project}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Comparison feature not yet implemented[/yellow]")


# ── Jira commands ─────────────────────────────────────────────────────────────

@jira_app.command("create")
def jira_create(
    project: str = typer.Option(..., "--project", "-p", help="Project name"),
    requirement: str = typer.Option(..., "--requirement", "-r", help="Requirement description"),
):
    """Create a Jira task from a requirement."""
    setup_logging()
    console.print(f"[bold]Creating Jira task for [cyan]{project}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Jira Task Agent not yet implemented[/yellow]")


@jira_app.command("bulk-create")
def jira_bulk_create(
    project: str = typer.Option(..., "--project", "-p", help="Project name"),
    file: str = typer.Option(..., "--file", "-f", help="YAML file with requirements list"),
):
    """Create multiple Jira tasks from a requirements file."""
    console.print(f"[bold]Bulk creating Jira tasks for [cyan]{project}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Bulk creation not yet implemented[/yellow]")


# ── Compliance commands ───────────────────────────────────────────────────────

@compliance_app.command("check")
def compliance_check(
    ticket: str = typer.Option(..., "--ticket", "-t", help="Jira ticket ID (e.g., PROJ-1234)"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix missing labels and tags"),
):
    """Check ICE compliance for a Jira ticket."""
    setup_logging()
    console.print(f"[bold]Checking ICE compliance for [cyan]{ticket}[/cyan]...[/bold]")
    console.print("[yellow]⚠ ICE Compliance Agent not yet implemented[/yellow]")


# ── Release commands ──────────────────────────────────────────────────────────

@release_app.command("prepare")
def release_prepare(
    ticket: str = typer.Option(..., "--ticket", "-t", help="Jira ticket ID"),
):
    """Prepare release documentation for a ticket."""
    setup_logging()
    console.print(f"[bold]Preparing release for [cyan]{ticket}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Release Prep Agent not yet implemented[/yellow]")


# ── PVT commands ──────────────────────────────────────────────────────────────

@pvt_app.command("run")
def pvt_run(
    project: str = typer.Option(..., "--project", "-p", help="Project name"),
):
    """Run PVT health check for a project."""
    setup_logging()
    console.print(f"[bold]Running PVT health check for [cyan]{project}[/cyan]...[/bold]")
    console.print("[yellow]⚠ PVT Agent not yet implemented[/yellow]")


# ── Docs commands ─────────────────────────────────────────────────────────────

@docs_app.command("search")
def docs_search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search Confluence documentation."""
    setup_logging()
    console.print(f"[bold]Searching docs for: [cyan]{query}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Doc Retriever Agent not yet implemented[/yellow]")


# ── Alert commands ────────────────────────────────────────────────────────────

@alert_app.command("triage")
def alert_triage(
    service: str = typer.Option(..., "--service", "-s", help="Service name"),
):
    """Triage a production alert for a service."""
    setup_logging()
    console.print(f"[bold]Triaging alert for [cyan]{service}[/cyan]...[/bold]")
    console.print("[yellow]⚠ Log Analyst Agent not yet implemented[/yellow]")


if __name__ == "__main__":
    app()
