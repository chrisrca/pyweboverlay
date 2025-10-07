import threading
import uuid
import os
import logging
import sys
import time
from io import StringIO
from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO, Namespace
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger('pyweboverlay')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Global app and socketio instances
app = Flask(__name__)
socketio = SocketIO(app)

# Registry for overlays
overlays = {}
overlay_names = set()
name_to_overlay = {}
server_port = 5000
verbose = True  # Global verbose flag

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

class PyWebOverlay:
    @staticmethod
    def init(port: int = 5000, verbose: bool = True) -> None:
        """
        Initialize the pyweboverlay library by starting a local web server in a background thread.

        Args:
            port (int): Port for the web server (default: 5000).
            verbose (bool): If True, print detailed logs; if False, minimize output (default: True).
        """
        global server_port
        server_port = port
        globals()['verbose'] = verbose

        # Configure Flask and SocketIO logging
        if not verbose:
            # Suppress Flask/Werkzeug, SocketIO, and EngineIO logs
            logging.getLogger('werkzeug').disabled = True  # Disable Werkzeug logger entirely
            logging.getLogger('socketio').setLevel(logging.ERROR)
            logging.getLogger('engineio').setLevel(logging.ERROR)
            # Suppress pyweboverlay logs
            logger.setLevel(logging.ERROR)
            # Suppress Flask's app startup message
            app.logger.disabled = True
            logging.getLogger('flask').setLevel(logging.ERROR)
            # Override Flask's server banner function to suppress startup messages
            import flask.cli
            flask.cli.show_server_banner = lambda *args: None
        else:
            logger.setLevel(logging.INFO)
            app.logger.disabled = False
            logging.getLogger('flask').setLevel(logging.INFO)
            logging.getLogger('werkzeug').disabled = False

        def run_server():
            # Pass log_output=False to suppress Flask's default console output
            socketio.run(
                app,
                port=port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True,
                log_output=verbose  # Only log to console if verbose=True
            )

        # Start server in a daemon thread
        threading.Thread(target=run_server, daemon=True).start()
        
        # Give the server time to fully start before returning
        time.sleep(1)
        
        if verbose:
            logger.info(f"PyWebOverlay server started at http://localhost:{port}")

    @staticmethod
    def register(overlay: Overlay, name: str, template_file: str = None, static_dir: str = None) -> str:
        """
        Register an overlay instance with the server.

        Args:
            overlay: An instance of a class extending Overlay.
            name: Custom name for the overlay's namespace.
            template_file: Optional path to a custom HTML template file.
            static_dir: Optional path to a directory for serving static files.
        """
        if not isinstance(overlay, Overlay):
            raise ValueError("Overlay must be an instance of a class extending Overlay")
        
        if not name:
            raise ValueError("Name is required for registration")
        
        if name in overlay_names:
            raise ValueError(f"Overlay name '{name}' is already in use")
        
        overlay_id = overlay.id
        namespace = f"/{name}"
        overlays[overlay_id] = overlay
        overlay_names.add(name)
        name_to_overlay[name] = overlay
        
        socketio.on_namespace(OverlayNamespace(overlay, namespace))
        
        if template_file:
            with open(template_file, 'r') as f:
                template_str = f.read()
        else:
            template_str = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>PyWebOverlay {{ name }}</title>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
                    <style> body { background: transparent; color: white; font-family: Arial; } </style>
                </head>
                <body>
                    <h1>{{ name }} Overlay</h1>
                    <p>Data: <span id="data">Waiting...</span></p>
                    <script>
                        const socket = io('http://localhost:{{ port }}{{ namespace }}');
                        socket.on('update', data => {
                            document.getElementById('data').textContent = JSON.stringify(data);
                        });
                    </script>
                </body>
                </html>
            """
        
        def make_overlay_route(template, overlay_name, overlay_namespace):
            def route_func():
                return render_template_string(template, name=overlay_name, namespace=overlay_namespace, port=server_port)
            return route_func
        
        def make_static_route(static_directory):
            def route_func(filename):
                if verbose:
                    logger.info(f"Attempting to serve static file: {static_directory}/{filename}")
                return send_from_directory(static_directory, filename)
            return route_func
        
        overlay_route_func = make_overlay_route(template_str, name, namespace)
        overlay_route_func.__name__ = f'overlay_route_{name}'
        app.add_url_rule(f'/{name}', f'overlay_route_{name}', overlay_route_func)
        
        if static_dir:
            static_dir = os.path.abspath(static_dir)
            if verbose:
                logger.info(f"Registering static route for absolute path: {static_dir}")
            static_route_func = make_static_route(static_dir)
            static_route_func.__name__ = f'serve_static_{name}'
            app.add_url_rule(f'/{name}/static/<path:filename>', f'serve_static_{name}', static_route_func)
        
        if verbose:
            logger.info(f"Registered overlay {overlay_id} with namespace {namespace}")
        return overlay_id

    @staticmethod
    def update(name: str, data: any = None) -> None:
        """
        Update the overlay with new data and emit to clients.

        Args:
            name: The registered name of the overlay.
            data: Data to pass to the overlay's update method.
        """
        if name not in name_to_overlay:
            raise ValueError(f"Overlay '{name}' not registered")
        
        overlay = name_to_overlay[name]
        overlay.update(data)
        socketio.emit('update', overlay.get_data(), namespace=f'/{name}')

@app.route('/')
def index():
    return "PyWebOverlay Server", 200

init = PyWebOverlay.init
register = PyWebOverlay.register
update = PyWebOverlay.update