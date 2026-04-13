"""
Agent Identity Generator
========================
Programmatically generates unique pixel art agent avatars
with randomized colors and a generated name.

Each run produces a different agent identity, allowing
a fleet of unique agents to be deployed over time.
"""

import os
import random
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw


# ── Name components ──────────────────────────────────────────────────

PREFIXES = [
    "Nano", "Pixel", "Byte", "Cipher", "Nova", "Flux", "Echo",
    "Axiom", "Qubit", "Zeta", "Helix", "Neon", "Pulse", "Vega",
    "Apex", "Rune", "Orbit", "Sigma", "Delta", "Proto",
]

SUFFIXES = [
    "Bot", "Node", "Agent", "Core", "Eye", "Watcher", "Scout",
    "Probe", "Lens", "Guard", "Trace", "Verif", "Audit", "Check",
    "Scan", "Hawk", "Sentry", "Spark", "Drift", "Sync",
]


def generate_agent_name(seed: int = None) -> str:
    """Generate a random agent name from prefix + suffix combos."""
    rng = random.Random(seed)
    prefix = rng.choice(PREFIXES)
    suffix = rng.choice(SUFFIXES)
    number = rng.randint(10, 99)
    return f"{prefix}{suffix}-{number}"


# ── Color palettes ───────────────────────────────────────────────────

SKIN_TONES = [
    (255, 220, 177),  # light
    (241, 194, 125),  # warm
    (198, 134, 66),   # medium
    (141, 85, 36),    # dark
    (80, 50, 20),     # deep
    (200, 200, 255),  # cyber blue
    (180, 255, 180),  # matrix green
    (255, 180, 255),  # synthwave pink
]

EYE_COLORS = [
    (0, 120, 255),    # electric blue
    (0, 220, 100),    # matrix green
    (255, 50, 50),    # red alert
    (255, 200, 0),    # golden
    (200, 0, 255),    # violet
    (0, 255, 255),    # cyan
    (255, 128, 0),    # orange
    (255, 255, 255),  # white
]

BACKGROUNDS = [
    (10, 10, 30),     # deep space
    (0, 20, 40),      # dark ocean
    (20, 0, 40),      # deep purple
    (0, 30, 20),      # dark forest
    (30, 10, 0),      # dark ember
    (15, 15, 15),     # near black
    (5, 25, 35),      # midnight blue
    (25, 5, 25),      # dark magenta
]

ACCENT_COLORS = [
    (0, 255, 200),    # teal
    (255, 100, 0),    # orange
    (180, 0, 255),    # purple
    (255, 220, 0),    # yellow
    (0, 200, 255),    # sky
    (255, 50, 150),   # pink
    (100, 255, 50),   # lime
    (255, 255, 255),  # white
]


def _random_color(palette: list, rng: random.Random) -> tuple:
    return rng.choice(palette)


def generate_agent_image(output_path: str, seed: int = None) -> str:
    """
    Generate a unique pixel art agent avatar.

    Creates a 16x16 pixel art face then scales it up to 256x256
    for a clean retro look. Colors are seeded for reproducibility.

    Args:
        output_path: Where to save the generated image
        seed: Optional seed for reproducible generation

    Returns:
        The output path of the saved image
    """
    if seed is None:
        seed = random.randint(0, 999999)

    rng = random.Random(seed)

    # Canvas size — work at 16x16, scale up
    SIZE = 16
    SCALE = 16  # final image = 256x256

    img = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(img)

    # Pick colors
    bg = _random_color(BACKGROUNDS, rng)
    skin = _random_color(SKIN_TONES, rng)
    eye = _random_color(EYE_COLORS, rng)
    accent = _random_color(ACCENT_COLORS, rng)

    # Fill background
    draw.rectangle([0, 0, SIZE, SIZE], fill=bg)

    # ── Face ─────────────────────────────────────────────────────────
    # Head — centered oval-ish shape using a rectangle with rounded feel
    head_x1, head_y1 = 4, 3
    head_x2, head_y2 = 11, 13
    draw.rectangle([head_x1, head_y1, head_x2, head_y2], fill=skin)

    # Round the corners manually (pixel style)
    draw.point([(head_x1, head_y1)], fill=bg)
    draw.point([(head_x2, head_y1)], fill=bg)
    draw.point([(head_x1, head_y2)], fill=bg)
    draw.point([(head_x2, head_y2)], fill=bg)

    # ── Eyes ─────────────────────────────────────────────────────────
    # Left eye
    draw.rectangle([5, 6, 6, 7], fill=eye)
    # Right eye
    draw.rectangle([9, 6, 10, 7], fill=eye)

    # Eye shine (white pixel highlight)
    draw.point([(5, 6)], fill=(255, 255, 255))
    draw.point([(9, 6)], fill=(255, 255, 255))

    # ── Mouth ────────────────────────────────────────────────────────
    mouth_style = rng.choice(["smile", "flat", "smirk"])
    if mouth_style == "smile":
        draw.point([(6, 10)], fill=accent)
        draw.point([(7, 11)], fill=accent)
        draw.point([(8, 11)], fill=accent)
        draw.point([(9, 10)], fill=accent)
    elif mouth_style == "flat":
        draw.rectangle([6, 10, 9, 10], fill=accent)
    else:  # smirk
        draw.point([(7, 10)], fill=accent)
        draw.point([(8, 10)], fill=accent)
        draw.point([(9, 9)], fill=accent)

    # ── Antenna / headgear (random) ──────────────────────────────────
    headgear = rng.choice(["antenna", "horns", "none", "halo"])
    if headgear == "antenna":
        draw.line([(7, 3), (7, 1)], fill=accent)
        draw.point([(7, 0)], fill=eye)
    elif headgear == "horns":
        draw.point([(5, 2)], fill=accent)
        draw.point([(10, 2)], fill=accent)
    elif headgear == "halo":
        draw.rectangle([5, 1, 10, 1], fill=(255, 220, 0))

    # ── Neck / body hint ─────────────────────────────────────────────
    draw.rectangle([7, 13, 8, 14], fill=skin)
    draw.rectangle([5, 14, 10, 15], fill=accent)

    # Scale up for crisp pixel art look
    img_scaled = img.resize((SIZE * SCALE, SIZE * SCALE), Image.NEAREST)

    # Save
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    img_scaled.save(output_path, "JPEG", quality=95)

    return output_path


def create_unique_agent(output_dir: str = ".") -> dict:
    """
    Generate a complete unique agent identity — name + image.

    Returns a dict with:
        name: str       — the agent's generated name
        image_path: str — path to the saved image
        seed: int       — seed used (for reproducibility)
    """
    seed = random.randint(0, 999999)
    name = generate_agent_name(seed)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"agent_{name.lower().replace('-', '_')}_{timestamp}.jpg"
    image_path = os.path.join(output_dir, filename)

    generate_agent_image(image_path, seed=seed)

    return {
        "name": name,
        "image_path": image_path,
        "seed": seed,
    }