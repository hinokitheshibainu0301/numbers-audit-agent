from agent.fetcher import fetch_dia_metadata

# Known aliases for 中時新聞網 on the Numbers Protocol platform
CHINATIMES_KNOWN_ALIASES = {
    "infotimes.vs@gmail.com",
    "infotimes-2024",
    "infotimes_2024",
    "中時新聞網",
}


def verify_asset(pyro_asset: dict) -> dict:
    """
    Cross-reference a pyro asset against the DIA Backend API.

    Verification checks:
    - Nid exists and matches in DIA Backend
    - Asset is published and publicly accessible
    - Asset has on-chain integrity records on Numbers Mainnet
    - Title (headline) matches
    - Creator belongs to known 中時新聞網 aliases
    - Upload timestamp matches

    Returns a verification result dict.
    """
    nid = pyro_asset.get("assetNid")
    result = {
        "nid": nid,
        "title": pyro_asset.get("title", "Unknown"),
        "status": "UNVERIFIED",
        "mismatches": [],
        "checks_passed": [],
        "dia_data": None,
    }

    # Fetch from DIA Backend
    dia = fetch_dia_metadata(nid)

    if dia is None:
        result["status"] = "FAILED"
        result["mismatches"].append("Asset not found in DIA Backend")
        return result

    result["dia_data"] = dia

    # ── Check 1: Nid matches ─────────────────────────────────────────
    dia_nid = dia.get("id") or dia.get("cid")
    if dia_nid == nid:
        result["checks_passed"].append("nid_match")
    else:
        result["mismatches"].append(f"Nid mismatch: pyro='{nid}' vs dia='{dia_nid}'")

    # ── Check 2: Published and publicly accessible ───────────────────
    if dia.get("published") is True and dia.get("public_access") is True:
        result["checks_passed"].append("published_and_public")
    else:
        result["mismatches"].append(
            f"Not public: published={dia.get('published')} public_access={dia.get('public_access')}"
        )

    # ── Check 3: On-chain integrity records exist ────────────────────
    integrity_info = dia.get("integrity_info", [])
    if integrity_info and len(integrity_info) > 0:
        result["checks_passed"].append("on_chain_integrity")
        result["blockchain"] = integrity_info[0].get("explorer_url", "")
    else:
        result["mismatches"].append("No on-chain integrity records found")

    # ── Check 4: Headline (title) matches ───────────────────────────
    dia_headline = dia.get("headline", "")
    pyro_title = pyro_asset.get("title", "")
    if dia_headline.strip().lower() == pyro_title.strip().lower():
        result["checks_passed"].append("title_match")
    else:
        result["mismatches"].append(
            f"Title mismatch: pyro='{pyro_title}' vs dia='{dia_headline}'"
        )

    # ── Check 5: Creator is known 中時新聞網 alias ──────────────────
    dia_creator = (dia.get("creator") or "").strip().lower()
    dia_creator_name = (dia.get("creator_name") or "").strip().lower()
    dia_display_name = (dia.get("creator_profile_display_name") or "").strip().lower()

    known = {a.lower() for a in CHINATIMES_KNOWN_ALIASES}
    if any(v in known for v in [dia_creator, dia_creator_name, dia_display_name]):
        result["checks_passed"].append("creator_verified")
    else:
        result["mismatches"].append(
            f"Unknown creator: '{dia.get('creator')}' / '{dia.get('creator_profile_display_name')}'"
        )

    # ── Check 6: Upload timestamp matches ───────────────────────────
    dia_uploaded = (dia.get("uploaded_at") or "")[:19]   # trim microseconds
    pyro_uploaded = (pyro_asset.get("uploadedAt") or "")[:19]
    if dia_uploaded and pyro_uploaded and dia_uploaded == pyro_uploaded:
        result["checks_passed"].append("timestamp_match")
    else:
        result["mismatches"].append(
            f"Timestamp mismatch: pyro='{pyro_uploaded}' vs dia='{dia_uploaded}'"
        )

    # ── Final verdict ────────────────────────────────────────────────
    if not result["mismatches"]:
        result["status"] = "VERIFIED"
    else:
        result["status"] = "MISMATCH"

    return result