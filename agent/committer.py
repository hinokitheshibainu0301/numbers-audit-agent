import os
import json
import time
import hashlib
import mimetypes
import requests
from datetime import datetime, timezone
from config import settings


def create_verification_commit(verification_result: dict) -> dict:
    """
    Write an on-chain commit to the AGENT's asset history on Numbers Mainnet.

    Commits are anchored to the agent's own Nid (AGENT_NID), not the 中時 asset.
    This means all verification activity accumulates in one place — the agent's
    complete audit trail — queryable by looking up the agent's asset history.

    The 中時 asset Nid being audited is recorded in the custom payload.
    """
    audited_nid = verification_result["nid"]
    status = verification_result["status"]
    title = verification_result.get("title", "Unknown")
    mismatches = verification_result.get("mismatches", [])
    checks_passed = verification_result.get("checks_passed", [])

    abstract = (
        f"[{settings.AGENT_NAME}] Audited: '{title}' — {status}"
    )

    commit_data = {
        "assetCid": settings.AGENT_NID,        # ← commits go on the AGENT
        "encodingFormat": "application/json",
        "assetTimestampCreated": int(time.time()),
        "assetCreator": settings.AGENT_NAME,
        "assetSha256": settings.AGENT_NID,
        "abstract": abstract,
        "commitMessage": f"Provenance audit: {status}",
        "action": settings.ACTION_COMMIT_NID,
        "custom": json.dumps({
            "agent_name": settings.AGENT_NAME,
            "agent_nid": settings.AGENT_NID,
            "agent_wallet": settings.CAPTURE_WALLET,
            "audited_asset_nid": audited_nid,   # ← 中時 asset recorded here
            "audited_asset_title": title,
            "verification_status": status,
            "checks_passed": checks_passed,
            "mismatches": mismatches,
            "source_page": "https://x402-chinatimes.numbersprotocol.io/",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }),
    }

    try:
        response = requests.post(
            settings.COMMIT_API_URL,
            json=commit_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {settings.CAPTURE_TOKEN}",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "tx_hash": data.get("txHash"),
            "explorer_url": f"{data.get('explorer', '')}/{data.get('txHash', '')}",
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
        }


def _compute_proof_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of file bytes."""
    return hashlib.sha256(file_bytes).hexdigest()


def _find_existing_asset_by_hash(proof_hash: str) -> str | None:
    """
    Search the user's registered assets for one matching the given proof_hash.
    Returns the Nid if found, None otherwise.

    Queries: GET https://api.numbersprotocol.io/api/v3/assets/
    Then filters locally by proof_hash field.
    """
    headers = {"Authorization": f"token {settings.CAPTURE_TOKEN}"}
    offset = 0
    limit = 200

    while True:
        try:
            response = requests.get(
                "https://api.numbersprotocol.io/api/v3/assets/",
                headers=headers,
                params={"limit": limit, "offset": offset},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # API may return a list or a dict with results
            assets = data if isinstance(data, list) else data.get("results", [])

            for asset in assets:
                if asset.get("proof_hash") == proof_hash:
                    return asset.get("id")

            # Paginate if needed
            if len(assets) < limit:
                break
            offset += limit

        except requests.RequestException:
            break

    return None


def register_agent_image(image_path: str, agent_name: str = None) -> tuple[str | None, bool]:
    """
    Register an agent identity image on Numbers Protocol.

    First checks if the file has already been registered by computing
    its SHA-256 proof_hash and searching existing assets.

    The agent_name is used as the headline of the registered asset,
    making it identifiable on Numbers Mainnet by name.

    Returns:
        (nid, was_existing) — Nid of the asset and whether it already existed.
        Returns (None, False) on failure.

    Registration endpoint: POST https://api.numbersprotocol.io/api/v3/assets/
    Cost: 0.1 NUM per call + gas (only charged on fresh registration)
    """
    name = agent_name or settings.AGENT_NAME

    try:
        with open(image_path, "rb") as f:
            file_bytes = f.read()

        proof_hash = _compute_proof_hash(file_bytes)
        mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
        filename = os.path.basename(image_path)

        # ── Step 1: Check if already registered ─────────────────────
        existing_nid = _find_existing_asset_by_hash(proof_hash)
        if existing_nid:
            return existing_nid, True

        # ── Step 2: Register fresh ───────────────────────────────────
        signed_metadata = json.dumps({
            "proof_hash": proof_hash,
            "asset_mime_type": mime_type,
            "created_at": int(time.time()),
        })

        files = {
            "asset_file": (filename, file_bytes, mime_type),
        }
        data = {
            "caption": f"{name} — AI Audit Agent for Numbers Protocol x402",
            "headline": name[:25],                  # ← agent name as headline
            "signed_metadata": signed_metadata,
        }
        headers = {
            "Authorization": f"token {settings.CAPTURE_TOKEN}",
        }

        response = requests.post(
            "https://api.numbersprotocol.io/api/v3/assets/",
            files=files,
            data=data,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()

        return result.get("id"), False

    except Exception:
        return None, False