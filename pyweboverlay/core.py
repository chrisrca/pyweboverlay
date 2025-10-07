import threading
import os
import logging
import time
from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO
from .overlay import Overlay, OverlayNamespace

# Configure logging
logger = logging.getLogger('pyweboverlay')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Global app and socketio instances
app = Flask(__name__, static_folder=None)
socketio = SocketIO(app)

# Registry for overlays
overlays = {}
overlay_names = set()
name_to_overlay = {}
server_port = 5000
verbose = True
static_dirs = {}

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

        if not verbose:
            logging.getLogger('werkzeug').disabled = True
            logging.getLogger('socketio').setLevel(logging.ERROR)
            logging.getLogger('engineio').setLevel(logging.ERROR)
            logger.setLevel(logging.ERROR)
            app.logger.disabled = True
            logging.getLogger('flask').setLevel(logging.ERROR)
            import flask.cli
            flask.cli.show_server_banner = lambda *args: None
        else:
            logger.setLevel(logging.INFO)
            app.logger.disabled = False
            logging.getLogger('flask').setLevel(logging.INFO)
            logging.getLogger('werkzeug').disabled = False

        def run_server():
            socketio.run(
                app,
                port=port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True,
                log_output=verbose
            )

        threading.Thread(target=run_server, daemon=True).start()
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
            # Load default template from file
            template_path = os.path.join(os.path.dirname(__file__), 'template.html')
            with open(template_path, 'r') as f:
                template_str = f.read()
        
        def make_overlay_route(template, overlay_name, overlay_namespace):
            def route_func():
                return render_template_string(template, name=overlay_name, namespace=overlay_namespace, port=server_port)
            return route_func
        
        overlay_route_func = make_overlay_route(template_str, name, namespace)
        overlay_route_func.__name__ = f'overlay_route_{name}'
        app.add_url_rule(f'/{name}', f'overlay_route_{name}', overlay_route_func)
        
        if static_dir:
            static_dir = os.path.abspath(static_dir)
            static_dirs[name] = static_dir
            if verbose:
                logger.info(f"Registered static directory for {name}: {static_dir}")
            
            # Add overlay specific static route
            def make_static_route(static_directory, overlay_name):
                def route_func(filename):
                    file_path = os.path.join(static_directory, filename)
                    if os.path.exists(file_path):
                        if verbose:
                            logger.info(f"Serving static file from {overlay_name}: {file_path}")
                        return send_from_directory(static_directory, filename)
                    if verbose:
                        logger.warning(f"Static file not found in {overlay_name}: {file_path}")
                    return "File not found", 404
                return route_func
            
            static_route_func = make_static_route(static_dir, name)
            static_route_func.__name__ = f'serve_static_{name}'
            app.add_url_rule(f'/{name}/static/<path:filename>', f'serve_static_{name}', static_route_func)
        
        # Register global /static/ route
        # NOTE: Must be registered BEFORE overlay route to take precedence
        if static_dir and not hasattr(app, 'global_static_registered'):
            def global_static_route_func(filename):
                v = globals().get('verbose', True)
                logger.info(f"Global static route called for {filename}")
                # Try to find the file in any registered static directory
                for _, static_directory in static_dirs.items():
                    file_path = os.path.join(static_directory, filename)
                    if v:
                        logger.info(f"Looking for /static/{filename} in {static_directory}: {file_path}")
                        logger.info(f"File exists: {os.path.exists(file_path)}")
                    if os.path.exists(file_path):
                        if v:
                            logger.info(f"Serving static file from /static/: {file_path}")
                        return send_from_directory(static_directory, filename)
                if v:
                    logger.warning(f"Static file not found in /static/: {filename}")
                    logger.warning(f"Searched in directories: {list(static_dirs.values())}")
                return "File not found", 404
            
            global_static_route_func.__name__ = 'serve_global_static'
            app.add_url_rule('/static/<path:filename>', 'serve_global_static', global_static_route_func)
            app.global_static_registered = True
            if verbose:
                logger.info(f"Registered global /static/ route")
                logger.info(f"Static directories available: {static_dirs}")
                # List all routes to debug
                logger.info("All registered routes:")
                for rule in app.url_map.iter_rules():
                    logger.info(f"  {rule.rule} -> {rule.endpoint}")
        
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