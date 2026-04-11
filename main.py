"""
Numbers Protocol Audit Agent
============================
Fetches all assets from the China Times x402 showcase page,
verifies their provenance against the DIA Backend API,
and records each verification as an immutable on-chain commit
on Numbers Mainnet.

Usage:
    python main.py              # Full run with on-chain commits
    python main.py --dry-run    # Verification only, no commits
"""

import os
import sys
import time
import argparse
from rich.prompt import Prompt

from config import settings
from agent.fetcher import fetch_all_assets
from agent.verifier import verify_asset
from agent.committer import create_verification_commit, register_agent_image
from agent import reporter as ui


def parse_args():
    parser = argparse.ArgumentParser(description="Numbers Protocol Audit Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run verification only — no on-chain commits will be made",
    )
    return parser.parse_args()


def resolve_agent_identity() -> str:
    if settings.AGENT_NID:
        ui.print_success("Agent identity loaded from config")
        ui.print_info(f"Agent name: [bold]{settings.AGENT_NAME}[/bold]")
        ui.print_info(f"Agent Nid:  [dim]{settings.AGENT_NID[:30]}...[/dim]")
        return settings.AGENT_NID

    ui.print_warning("No AGENT_NID found in environment.")
    ui.console.print(
        "\n[bold]Let's set up your agent's on-chain identity.[/bold]\n"
        "[dim]This image and name will be registered on Numbers Mainnet.[/dim]\n"
    )

    # Prompt for agent name first
    agent_name = Prompt.ask(
        "Enter a name for your agent",
        default=settings.AGENT_NAME,
    )
    settings.AGENT_NAME = agent_name

    # Prompt for image
    image_path = Prompt.ask("Enter path to agent image (PNG/JPG)")

    if not os.path.exists(image_path):
        ui.print_error(f"File not found: {image_path}")
        sys.exit(1)

    ui.print_chain("Checking if image is already registered on Numbers Mainnet...")
    nid, was_existing = register_agent_image(image_path, agent_name)

    if not nid:
        ui.print_error("Failed to register agent image. Check your CAPTURE_TOKEN and try again.")
        sys.exit(1)

    if was_existing:
        ui.print_success(f"Found existing registration — reusing Nid: [bold]{nid}[/bold]")
    else:
        ui.print_success(f"Agent [bold]{agent_name}[/bold] registered on Numbers Mainnet!")

    ui.console.print(
        f"\n[bold yellow]Important:[/bold yellow] Add these to your .env to skip setup next time:\n"
        f"[bold]AGENT_NID={nid}[/bold]\n"
        f"[bold]AGENT_NAME={agent_name}[/bold]\n"
    )

    settings.AGENT_NID = nid
    return nid


def run(dry_run: bool = False):
    ui.print_banner()

    if dry_run:
        ui.console.print(
            "[bold yellow]⚠️  DRY RUN MODE — No on-chain commits will be made[/bold yellow]\n"
        )

    time.sleep(0.5)

    # Step 1: Agent identity
    ui.print_step("[bold]STEP 1[/bold] — Resolving agent identity...")
    if dry_run:
        agent_nid = settings.AGENT_NID or "DRY-RUN-NO-NID"
        ui.print_warning("Dry run — skipping agent registration check")
    else:
        agent_nid = resolve_agent_identity()
    ui.print_divider()
    time.sleep(0.3)

    # Step 2: Fetch assets
    ui.print_step("[bold]STEP 2[/bold] — Connecting to China Times x402 showcase...")
    time.sleep(0.5)

    try:
        assets = fetch_all_assets()
    except Exception as e:
        ui.print_error(f"Failed to fetch assets: {e}")
        sys.exit(1)

    ui.print_success(f"Connected. [bold]{len(assets)}[/bold] assets discovered.")
    ui.print_divider()
    time.sleep(0.3)

    # Step 3: Verify
    ui.print_step("[bold]STEP 3[/bold] — Beginning provenance verification sweep...")
    ui.console.print()

    results = []
    commits = []
    total = len(assets)

    for i, asset in enumerate(assets, start=1):
        result = verify_asset(asset)
        results.append(result)

        commit = None
        if not dry_run and result["status"] in ("VERIFIED", "MISMATCH"):
            commit = create_verification_commit(result)
        commits.append(commit)

        ui.print_asset_result(i, total, result, commit, dry_run=dry_run)
        time.sleep(0.2)

    # Step 4: Summary
    ui.print_divider()
    ui.print_step("[bold]STEP 4[/bold] — Audit complete.")
    ui.print_summary(results, commits, dry_run=dry_run)

    if not dry_run:
        ui.console.print(
            f"\n[bold cyan]🎉 Full agent activity recorded on Numbers Mainnet.[/bold cyan]\n"
            f"[dim]Agent Nid: {agent_nid}[/dim]\n"
        )
    else:
        ui.console.print(
            "\n[bold yellow]Dry run complete. Run without --dry-run to write on-chain commits.[/bold yellow]\n"
        )


if __name__ == "__main__":
    args = parse_args()
    run(dry_run=args.dry_run)