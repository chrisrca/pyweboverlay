import pytest
import requests
import time
import pyweboverlay
import socket

@pytest.fixture(scope="function")
def web_server():
    """Fixture to start and manage the PyWebOverlay server."""
    test_port = 5001
    
    # Check if port is available
    def is_port_free(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    if not is_port_free(test_port):
        raise RuntimeError(f"Port {test_port} is already in use")
    
    # Start the server
    pyweboverlay.init(port=test_port)
    time.sleep(1)  # Wait for server to start
    
    yield test_port
    # Daemon thread terminates with test process, no explicit cleanup needed

def test_init(web_server):
    """Test that PyWebOverlay.init() starts the server correctly."""
    test_port = web_server
    try:
        response = requests.get(f"http://localhost:{test_port}", timeout=2)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert response.text == "PyWebOverlay Server", f"Unexpected response: {response.text}"
    except requests.ConnectionError:
        pytest.fail(f"Server failed to start or is not accessible on port {test_port}")