import logging
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from config import settings

console = Console()

# Setup file logging
log_path = Path("logs") / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_path,
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]NUMBERS PROTOCOL AUDIT AGENT[/bold cyan]\n"
        "[dim]Powered by x402 · China Times · Numbers Mainnet[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()


def print_step(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    console.print(f"[dim][{ts}][/dim] {message}")
    logger.info(message)


def print_success(message: str):
    print_step(f"[bold green]✅[/bold green] {message}")


def print_error(message: str):
    print_step(f"[bold red]❌[/bold red] {message}")


def print_warning(message: str):
    print_step(f"[bold yellow]⚠️ [/bold yellow]  {message}")


def print_info(message: str):
    print_step(f"[bold blue]🔍[/bold blue] {message}")


def print_chain(message: str):
    print_step(f"[bold magenta]⛓️ [/bold magenta] {message}")


def print_divider():
    console.print("[dim]" + "─" * 60 + "[/dim]")


def print_asset_result(index: int, total: int, result: dict, commit: dict = None, dry_run: bool = False):
    nid = result["nid"]
    title = result["title"]
    status = result["status"]
    short_nid = nid[:24] + "..." if nid else "N/A"

    if status == "VERIFIED":
        status_str = "[bold green]VERIFIED[/bold green]"
    elif status == "MISMATCH":
        status_str = "[bold yellow]MISMATCH[/bold yellow]"
    else:
        status_str = "[bold red]FAILED[/bold red]"

    ts = datetime.now().strftime("%H:%M:%S")
    console.print(
        f"[dim][{ts}][/dim] [[bold]{index}/{total}[/bold]] [bold]{title[:45]}[/bold]\n"
        f"         [dim]Nid: {short_nid}[/dim]\n"
        f"         Status: {status_str}"
    )

    for check in result.get("checks_passed", []):
        console.print(f"         [dim green]✓ {check}[/dim green]")

    for m in result.get("mismatches", []):
        console.print(f"         [dim red]✗ {m}[/dim red]")

    if result.get("blockchain"):
        console.print(f"         [dim blue]⛓  {result['blockchain']}[/dim blue]")

    if dry_run:
        console.print(f"         [dim yellow]⚡ Dry run — commit skipped[/dim yellow]")
    elif commit and commit.get("success"):
        console.print(f"         [dim magenta]📝 Tx: {commit.get('tx_hash', 'N/A')}[/dim magenta]")
    elif commit and not commit.get("success"):
        console.print(f"         [dim red]📝 Commit failed: {commit.get('error', 'Unknown')}[/dim red]")

    console.print()
    logger.info(f"[{index}/{total}] {title} | {status} | Nid: {nid}")
    if commit:
        logger.info(f"  Commit tx: {commit.get('tx_hash')} | Error: {commit.get('error')}")


def print_summary(results: list, commits: list, dry_run: bool = False):
    total = len(results)
    verified = sum(1 for r in results if r["status"] == "VERIFIED")
    mismatched = sum(1 for r in results if r["status"] == "MISMATCH")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    successful_commits = sum(1 for c in commits if c and c.get("success"))

    commit_line = (
        f"[bold yellow]On-chain commits:[/bold yellow]      Skipped (dry run)"
        if dry_run else
        f"[bold magenta]On-chain commits:[/bold magenta]      {successful_commits} / {total}"
    )

    console.print(Panel(
        f"[bold]Total assets scanned:[/bold]   {total}\n"
        f"[bold green]Verified:[/bold green]              {verified}\n"
        f"[bold yellow]Mismatched:[/bold yellow]            {mismatched}\n"
        f"[bold red]Failed:[/bold red]                {failed}\n"
        f"{commit_line}",
        title="[bold]AUDIT SUMMARY[/bold]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print(f"\n[dim]Full log saved to: {log_path}[/dim]")


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    )