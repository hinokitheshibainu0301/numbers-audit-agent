"""
Agent Registry
==============
Maintains a persistent JSON record of every agent run,
including agent identity, verification results, and timestamps.

The registry is committed back to the repo after each run
via GitHub Actions, creating a living campaign history.
"""

import json
import os
from datetime import datetime, timezone

REGISTRY_PATH = "registry.json"


def load_registry() -> list:
    """Load existing registry or return empty list."""
    if not os.path.exists(REGISTRY_PATH):
        return []
    try:
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_registry(registry: list) -> None:
    """Save registry to disk."""
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def record_run(
    agent_name: str,
    agent_nid: str,
    seed: int,
    results: list[dict],
    commits: list[dict],
) -> dict:
    """
    Append a new run entry to the registry and save.

    Returns the new entry.
    """
    registry = load_registry()

    verified = sum(1 for r in results if r["status"] == "VERIFIED")
    mismatched = sum(1 for r in results if r["status"] == "MISMATCH")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    successful_commits = sum(1 for c in commits if c and c.get("success"))

    entry = {
        "run": len(registry) + 1,
        "agent_name": agent_name,
        "agent_nid": agent_nid,
        "agent_explorer": f"https://mainnet.num.network/address/{agent_nid}",
        "seed": seed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": {
            "total": len(results),
            "verified": verified,
            "mismatched": mismatched,
            "failed": failed,
        },
        "commits": {
            "total": successful_commits,
        },
        "assets": [
            {
                "nid": r["nid"],
                "title": r["title"],
                "status": r["status"],
            }
            for r in results
        ],
    }

    registry.append(entry)
    save_registry(registry)
    return entry


def get_summary() -> dict:
    """Return high-level campaign summary stats."""
    registry = load_registry()
    if not registry:
        return {}

    total_runs = len(registry)
    total_agents = len({r["agent_nid"] for r in registry})
    total_commits = sum(r["commits"]["total"] for r in registry)
    total_verified = sum(r["results"]["verified"] for r in registry)

    return {
        "total_runs": total_runs,
        "total_unique_agents": total_agents,
        "total_on_chain_commits": total_commits,
        "total_verified": total_verified,
        "first_run": registry[0]["timestamp"],
        "latest_run": registry[-1]["timestamp"],
    }