import pytest
import requests
import time
import pyweboverlay

def test_init():
    """Test that PyWebOverlay.init() starts the server correctly."""
    test_port = 5001
    pyweboverlay.init(port=test_port)
    time.sleep(1)
    try:
        response = requests.get(f"http://localhost:{test_port}", timeout=2)
        assert response.status_code in [200, 404]
    except requests.ConnectionError:
        pytest.fail(f"Server failed to start on port {test_port}")