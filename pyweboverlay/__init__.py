"""
PyWebOverlay: A library for creating dynamic Twitch overlays in Python.
"""

__all__ = (
    "PyWebOverlay",
    "init",
    "register",
    "update",
    "Overlay",
    "OverlayNamespace",
)

__version__ = "1.0.5"

from .core import PyWebOverlay, init, register, update
from .overlay import Overlay, OverlayNamespace