#!/usr/bin/env python
# ============================================================
# main.py — CLI entry point
# Usage: python main.py [OPTIONS]
# ============================================================

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from scraper.core.orchestrator import run_scraper
from scraper.utils.logger import log

console = Console()


def print_banner():
    text = Text()
    text.append("BRACKEN & KFEM DIGITAL SOLUTIONS\n", style="bold white")
    text.append("Estate Lead Scraper — Production Grade\n", style="bold yellow")
    text.append("Powering smarter estate outreach across Nigeria.", style="dim white")
    console.print(Panel(text, border_style="blue", expand=False))


@click.group()
def cli():
    """Bracken & KFEM Estate Lead Scraper."""
    pass


@cli.command()
@click.option(
    "--states", "-s",
    default="lagos,abuja",
    help="Comma-separated states to scrape. E.g: lagos,abuja",
    show_default=True,
)
@click.option(
    "--session-id", "-id",
    default=None,
    help="Custom session ID (for resuming). Leave blank to auto-generate.",
)
@click.option(
    "--resume/--no-resume",
    default=True,
    help="Resume a previous session (default: true).",
    show_default=True,
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    help="Force headful mode and save extra debug dumps for each query.",
    show_default=True,
)
def scrape(states: str, session_id: str, resume: bool, verbose: bool):
    """Run the Google Maps estate scraper."""
    print_banner()
    state_list = [s.strip().capitalize() for s in states.split(",")]
    log.info(f"Starting scraper for states: {state_list}")

    if verbose:
        from config.settings import settings

        settings.SCRAPER_HEADLESS = False
        settings.SCRAPER_VERBOSE_DUMPS = True
        settings.SCRAPER_SLOW_MO = max(settings.SCRAPER_SLOW_MO, 200)
        settings.LOG_LEVEL = "DEBUG"
        log.info("Verbose mode enabled: headful browser, extra debug dumps, and slower pacing.")

    if not resume and session_id:
        from scraper.utils.progress_tracker import ProgressTracker
        pt = ProgressTracker(session_id)
        pt.reset()
        log.info(f"Progress reset for session '{session_id}'.")

    asyncio.run(run_scraper(states=state_list, session_id=session_id))


@cli.command()
@click.argument("json_file")
def rescore(json_file: str):
    """Re-score leads from a previously saved raw JSON file (no re-scraping)."""
    import json
    from pathlib import Path
    from scraper.core.models import EstateRecord
    from leads.scorer import score_all_records
    from scraper.exporters.exporter import export_to_excel, export_to_csv
    from datetime import datetime

    print_banner()
    path = Path(json_file)
    if not path.exists():
        console.print(f"[red]File not found: {json_file}[/red]")
        return

    raw = json.loads(path.read_text(encoding="utf-8"))
    records = [EstateRecord(**r) for r in raw]
    log.info(f"Loaded {len(records):,} records from {json_file}")

    records = score_all_records(records)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_to_csv(records, f"rescored_{ts}.csv")
    export_to_excel(records, f"rescored_{ts}.xlsx")
    log.info("Rescoring complete.")


@cli.command()
def stats():
    """Show statistics about the latest scraping session."""
    from pathlib import Path
    import json

    raw_dir = Path("data/raw")
    files = sorted(raw_dir.glob("raw_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        console.print("[yellow]No raw data files found.[/yellow]")
        return

    latest = files[0]
    records = json.loads(latest.read_text(encoding="utf-8"))

    hot = sum(1 for r in records if r.get("lead_tier") == "HOT")
    warm = sum(1 for r in records if r.get("lead_tier") == "WARM")
    cold = sum(1 for r in records if r.get("lead_tier") == "COLD")

    console.print(Panel(
        f"[bold]Latest file:[/bold] {latest.name}\n"
        f"[bold]Total records:[/bold] {len(records):,}\n"
        f"[bold red]🔥 HOT:[/bold red] {hot}\n"
        f"[bold yellow]🟡 WARM:[/bold yellow] {warm}\n"
        f"[bold blue]🔵 COLD:[/bold blue] {cold}",
        title="📊 Scraper Stats",
        border_style="green",
    ))


if __name__ == "__main__":
    cli()
