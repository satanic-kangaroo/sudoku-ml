"""
Client-side optimized image uploader.
The image is resized and compressed in the browser before being sent to Python.
"""

from pathlib import Path
import streamlit.components.v1 as components


# مسیر پوشه‌ی کامپوننت
_COMPONENT_DIR = Path(__file__).resolve().parent.parent / "components" / "image_uploader"

# ثبت کامپوننت (فقط یک بار در طول اجرا)
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
    Image uploader with client-side optimization.

    Args:
        max_dimension: حداکثر عرض یا ارتفاع (پیکسل).
        quality:       کیفیت JPEG (0.0 تا 1.0).
        key:           کلید یکتای Streamlit.

    Returns:
        dict یا None:
            bytes:          bytes — بایت‌های تصویر بهینه‌شده (JPEG)
            width:          int
            height:         int
            original_size:  int — بایت‌های فایل اصلی
            optimized_size: int — بایت‌های فایل بهینه‌شده
            mime_type:      str
            name:           str
    """
    result = _component_func(
        max_dimension=max_dimension,
        quality=quality,
        key=key,
        default=None,
    )
    return result