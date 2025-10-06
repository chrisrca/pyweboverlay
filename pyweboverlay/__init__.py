"""
PyWebOverlay: A library for creating dynamic Twitch overlays in Python.
"""

__all__ = (
    "PyWebOverlay",
    "init",
    "register",
    "update",
)

__version__ = "0.1.0"

from .core import PyWebOverlay, init, register, update