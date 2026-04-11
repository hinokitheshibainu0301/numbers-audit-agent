import requests
from config import settings


def fetch_all_assets() -> list[dict]:
    """
    Fetch all assets from the China Times x402 showcase page
    via the fetchPyroAssets API. Handles pagination automatically.
    """
    assets = []
    page = 1
    limit = 48

    while True:
        params = {
            "org_id": settings.PYRO_ORG_ID,
            "page": page,
            "limit": limit,
        }

        response = requests.get(settings.PYRO_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        batch = data.get("assets", [])
        assets.extend(batch)

        if not data.get("hasMore", False):
            break

        page += 1

    return assets


def fetch_dia_metadata(nid: str) -> dict | None:
    """
    Fetch asset metadata from the Numbers Protocol DIA Backend API.
    No auth required for public assets.
    """
    url = f"{settings.DIA_BACKEND_URL}/assets/{nid}/"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None