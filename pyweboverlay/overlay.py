from flask_socketio import Namespace
from abc import ABC, abstractmethod
import uuid

class Overlay(ABC):
    """Base class for all overlays."""
    def __init__(self):
        self.id = str(uuid.uuid4())

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def update(self, data=None):
        pass

class OverlayNamespace(Namespace):
    """SocketIO namespace for an overlay."""
    def __init__(self, overlay, namespace):
        super().__init__(namespace)
        self.overlay = overlay

    def on_connect(self):
        """Send initial overlay data to client on connect."""
        self.emit('update', self.overlay.get_data())
