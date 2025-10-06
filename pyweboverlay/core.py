import threading
from flask import Flask
from flask_socketio import SocketIO

# Global app and socketio instances
app = Flask(__name__)
socketio = SocketIO(app)

# Registry for overlays
overlays = {}

@app.route('/')
def index():
    """Default route to verify server is running."""
    return "PyWebOverlay Server", 200

class PyWebOverlay:
    @staticmethod
    def init(port: int = 5000) -> None:
        """
        Initialize the pyweboverlay library by starting a local web server in a background thread.

        Args:
            port (int): Port for the web server (default: 5000).

        Note:
            This starts a Flask development server for local use (e.g., OBS/Twitch overlays).
            The server is ready for registering overlays after initialization.
        """
        def run_server():
            socketio.run(app, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
        
        # Start server in a daemon thread to avoid blocking
        threading.Thread(target=run_server, daemon=True).start()
        print(f"PyWebOverlay server started at http://localhost:{port}")

# Expose init at module level
init = PyWebOverlay.init