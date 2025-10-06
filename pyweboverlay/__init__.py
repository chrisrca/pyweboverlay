"""PyWebOverlay: A library for creating dynamic Twitch overlays in Python.

Easily define and update overlays with text, images, and shapes for streaming.
No HTML/CSS knowledge required. Overlays are served as local webpages for use in OBS/Twitch.

For guides and examples, see https://github.com/your-username/pyweboverlay.
"""

__all__ = (
    "PyWebOverlay",
    "init",
)

__version__ = "0.1.0"

from .core import PyWebOverlay, init