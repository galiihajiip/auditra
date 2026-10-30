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


