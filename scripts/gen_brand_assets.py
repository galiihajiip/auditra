"""Generate centered logo icon + favicon assets from the original Auditra logo."""

from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "web" / "public"
ASSET_CANDIDATES = [
    ROOT.parent.parent
    / "Users"
    / "Hype"
    / ".cursor"
    / "projects"
    / "c-GALIH-CODING-AUDITRA"
    / "assets"
    / "c__Users_Hype_AppData_Roaming_Cursor_User_workspaceStorage_ffc17569747929d4856205e055d9ad5a_images_image-48943b5a-5746-4089-93d7-ca223336ee76.png",
    PUBLIC / "logo.png",
]

WHITE_THRESH = 248
# Include full magnifying-glass handle; text band starts ~50% height on 1024px master.
ICON_BOTTOM_RATIO = 0.535


def load_source() -> Image.Image:
    for path in ASSET_CANDIDATES:
        if path.exists():
            return Image.open(path).convert("RGB")
    raise FileNotFoundError("Logo source not found")


def is_content_pixel(r: int, g: int, b: int) -> bool:
    return not (r > WHITE_THRESH and g > WHITE_THRESH and b > WHITE_THRESH)


def stack_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    """Bounds of icon + AUDITRA wordmark (full vertical logo stack)."""
    w, h = img.size
    px = img.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            if is_content_pixel(*px[x, y]):
                xs.append(x)
                ys.append(y)

    if not xs:
        return 0, 0, w, h

    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    pad_x = int((right - left) * 0.06)
    pad_top = int((bottom - top) * 0.06)
    pad_bottom = int((bottom - top) * 0.14)

    return (
        max(0, left - pad_x),
        max(0, top - pad_top),
        min(w, right + pad_x),
        min(h, bottom + pad_bottom),
    )


