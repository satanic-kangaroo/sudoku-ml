"""
Client-side optimized image uploader.
Image is resized & compressed in the browser before reaching Python.
"""

import base64
from pathlib import Path
import streamlit.components.v1 as components


_COMPONENT_DIR = Path(__file__).resolve().parent.parent / "components" / "image_uploader"

_component_func = components.declare_component(
    "optimized_image_uploader",
    path=str(_COMPONENT_DIR),
)


def optimized_image_uploader(
    max_dimension: int = 1000,
    quality: float = 0.85,
    key: str | None = None,
):
    """
    Returns a dict with:
        bytes:          bytes  — decoded JPEG bytes (ready for cv2.imdecode)
        width, height:  int
        original_size:  int
        optimized_size: int
        mime_type:      str
        name:           str
    Or None if no image yet.
    """
    raw = _component_func(
        max_dimension=max_dimension,
        quality=quality,
        key=key,
        default=None,
    )

    if raw is None:
        return None

    # Decode base64 data URL → raw JPEG bytes
    data_url = raw.get("data_url", "")
    if "," in data_url:
        _, b64 = data_url.split(",", 1)
    else:
        b64 = data_url

    try:
        img_bytes = base64.b64decode(b64)
    except Exception:
        return None

    return {
        "bytes":          img_bytes,
        "width":          raw.get("width", 0),
        "height":         raw.get("height", 0),
        "original_size":  raw.get("original_size", 0),
        "optimized_size": raw.get("optimized_size", len(img_bytes)),
        "mime_type":      raw.get("mime_type", "image/jpeg"),
        "name":           raw.get("name", "image.jpg"),
    }