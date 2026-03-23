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
from rich.table import Table

from work_buddy.core.config import load_app_config, load_project_config, list_projects
from work_buddy.core.container import create_container
from work_buddy.core.logging import setup_logging, get_logger
from work_buddy.agents.coordinator import AgentCoordinator

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
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Running {test_type} tests for [cyan]{project}[/cyan]...[/bold]")

    result = coordinator.execute("test", project=project, test_type=test_type)

    if result.get("success"):
        console.print("[green]✓ Tests completed successfully[/green]")
        packages = result.get("result", {}).get("evidence_packages", [])
        if packages:
            console.print(f"  Evidence packages: {len(packages)}")
    else:
        console.print(f"[red]✗ Tests failed: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)


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
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Creating Jira task for [cyan]{project}[/cyan]...[/bold]")

    result = coordinator.execute("jira", project=project, requirement=requirement)

    if result.get("success"):
        tickets = result.get("result", {}).get("tickets", [])
        if tickets:
            for t in tickets:
                console.print(f"[green]✓ Created ticket: {t['key']} - {t['summary']}[/green]")
    else:
        console.print(f"[red]✗ Failed: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)


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
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Checking ICE compliance for [cyan]{ticket}[/cyan]...[/bold]")

    result = coordinator.execute("compliance", ticket=ticket)

    validation = result.get("result", {})
    if validation.get("valid"):
        console.print("[green]✓ Ticket is ICE compliant[/green]")
    else:
        gaps = validation.get("gaps", [])
        console.print(f"[yellow]⚠ {len(gaps)} compliance gaps found:[/yellow]")

        table = Table()
        table.add_column("Type", style="cyan")
        table.add_column("Issue")
        table.add_column("Remediation")

        for gap in gaps:
            table.add_row(gap.get("type", ""), gap.get("message", ""), gap.get("remediation", ""))

        console.print(table)

        if not fix:
            raise typer.Exit(1)


# ── Release commands ──────────────────────────────────────────────────────────

@release_app.command("prepare")
def release_prepare(
    ticket: str = typer.Option(..., "--ticket", "-t", help="Jira ticket ID"),
    repo_path: str = typer.Option(".", "--repo", "-r", help="Path to git repository"),
    since_tag: str = typer.Option("HEAD~10", "--since", help="Git tag/commit to start from"),
):
    """Prepare release documentation for a ticket."""
    setup_logging()
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Preparing release for [cyan]{ticket}[/cyan]...[/bold]")

    result = coordinator.execute(
        "release",
        ticket=ticket,
        repo_path=repo_path,
        since_tag=since_tag
    )

    if result.get("success"):
        console.print("[green]✓ Release documentation prepared and posted[/green]")
    else:
        reason = result.get("result", {}).get("reason", result.get("error", "Unknown error"))
        console.print(f"[yellow]⚠ Release prep incomplete: {reason}[/yellow]")
        raise typer.Exit(1)


# ── PVT commands ──────────────────────────────────────────────────────────────

@pvt_app.command("run")
def pvt_run(
    project: str = typer.Option(..., "--project", "-p", help="Project name"),
):
    """Run PVT health check for a project."""
    setup_logging()
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Running PVT health check for [cyan]{project}[/cyan]...[/bold]")

    result = coordinator.execute("pvt", project=project)

    if result.get("success"):
        report_path = result.get("result", {}).get("report_path")
        console.print(f"[green]✓ PVT completed[/green]")
        if report_path:
            console.print(f"  Report: {report_path}")
    else:
        console.print(f"[red]✗ PVT failed: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)


@pvt_app.command("schedule")
def pvt_schedule(
    project: str = typer.Option(None, "--project", "-p", help="Project name (all if not specified)"),
    enable: bool = typer.Option(None, "--enable/--disable", help="Enable or disable scheduled PVT"),
    cron: str = typer.Option(None, "--cron", "-c", help="Cron expression (e.g., '0 6 * * *')"),
    timezone: str = typer.Option(None, "--timezone", "-tz", help="Timezone (e.g., 'Asia/Shanghai')"),
):
    """Configure or view PVT schedule for projects."""
    from work_buddy.core.scheduler import get_scheduler_status
    from zoneinfo import ZoneInfo
    from croniter import croniter

    if project:
        # Show/configure specific project
        try:
            proj_config = load_project_config(project)
            schedule = proj_config.pvt_schedule

            console.print(f"\n[bold]PVT Schedule for {project}:[/bold]")
            console.print(f"  Enabled: {'[green]Yes[/green]' if schedule.enabled else '[red]No[/red]'}")
            console.print(f"  Cron: {schedule.cron}")
            console.print(f"  Timezone: {schedule.timezone}")

            if cron or timezone or enable is not None:
                console.print("\n[yellow]To update schedule, edit the project config file:[/yellow]")
                console.print(f"  configs/projects/{project}.yaml")

        except FileNotFoundError:
            console.print(f"[red]Project '{project}' not found[/red]")
            raise typer.Exit(1)
    else:
        # Show all projects with PVT schedules
        status = get_scheduler_status()

        table = Table(title="PVT Schedules")
        table.add_column("Project", style="cyan")
        table.add_column("Enabled")
        table.add_column("Cron")
        table.add_column("Timezone")
        table.add_column("Next Run")

        for proj_name, proj_status in status.get("projects", {}).items():
            enabled = "[green]Yes[/green]" if proj_status.get("enabled") else "[red]No[/red]"
            next_run = proj_status.get("next_run", "-") or "-"
            table.add_row(
                proj_name,
                enabled,
                proj_status.get("cron", "-"),
                proj_status.get("timezone", "-"),
                next_run[:19] if next_run and next_run != "-" else "-"
            )

        console.print(table)


@pvt_app.command("start-scheduler")
def pvt_start_scheduler():
    """Start the PVT scheduler daemon."""
    import asyncio
    from work_buddy.core.scheduler import start_scheduler
    from work_buddy.agents.log_analyst_agent import LogAnalystAgent
    from work_buddy.core.container import create_container

    setup_logging()
    config = load_app_config()
    container = create_container(config)

    async def run_pvt(project):
        """Run PVT for a project."""
        try:
            browser_agent = container.browser_test_agent
            opensearch = container.opensearch_service
            grafana = container.grafana_service

            agent = LogAnalystAgent(browser_agent, opensearch, grafana)
            return await agent.run_pvt_healthcheck(project)
        except Exception as e:
            logger.error(f"PVT failed for {project.name}: {e}")
            return None

    console.print("[bold]Starting PVT scheduler...[/bold]")

    enabled_count = start_scheduler(run_pvt)

    if enabled_count == 0:
        console.print("[yellow]No projects have PVT scheduling enabled[/yellow]")
        console.print("Enable scheduling in project config: pvt_schedule.enabled: true")
        return

    console.print(f"[green]Scheduler started with {enabled_count} project(s)[/green]")
    console.print("Press Ctrl+C to stop")

    try:
        # Keep the process running
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        from work_buddy.core.scheduler import stop_scheduler
        stop_scheduler()
        console.print("\n[yellow]Scheduler stopped[/yellow]")


# ── Docs commands ─────────────────────────────────────────────────────────────

@docs_app.command("search")
def docs_search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search Confluence documentation."""
    setup_logging()
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Searching docs for: [cyan]{query}[/cyan]...[/bold]")

    result = coordinator.execute("docs", query=query)

    if result.get("success"):
        answer = result.get("result", {}).get("answer", "")
        sources = result.get("result", {}).get("sources", [])

        console.print(Panel(answer, title="Answer", border_style="green"))

        if sources:
            console.print("\n[bold]Sources:[/bold]")
            for src in sources:
                console.print(f"  • {src}")
    else:
        console.print(f"[yellow]No results found or error: {result.get('error', 'Unknown')}[/yellow]")


@docs_app.command("summarize")
def docs_summarize(
    page_id: str = typer.Argument(..., help="Confluence page ID"),
):
    """Summarize a Confluence document."""
    setup_logging()
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Summarizing page: [cyan]{page_id}[/cyan]...[/bold]")

    result = coordinator.execute("docs", page_id=page_id)

    if result.get("success") and result.get("result"):
        summary = result["result"].get("summary", "")
        title = result["result"].get("title", "")
        console.print(Panel(summary, title=f"Summary: {title}", border_style="green"))
    else:
        console.print(f"[yellow]Could not summarize page: {result.get('error', 'Page not found')}[/yellow]")


# ── Alert commands ────────────────────────────────────────────────────────────

@alert_app.command("triage")
def alert_triage(
    service: str = typer.Option(..., "--service", "-s", help="Service name (project config)"),
    alert: str = typer.Option(None, "--alert", "-a", help="Alert details/message"),
):
    """Triage a production alert for a service."""
    setup_logging()
    config = load_app_config()
    container = create_container(config)
    coordinator = AgentCoordinator(container)

    console.print(f"[bold]Triaging alert for [cyan]{service}[/cyan]...[/bold]")

    result = coordinator.execute("alert", project=service, alert_details=alert or "Manual triage request")

    if result.get("success"):
        report_path = result.get("result", {}).get("report_path")
        console.print(f"[green]✓ Triage complete[/green]")
        if report_path:
            console.print(f"  Report: {report_path}")
    else:
        console.print(f"[red]✗ Triage failed: {result.get('error', 'Unknown error')}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
