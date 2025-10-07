# pyweboverlay

A Python package for easily creating web overlays in Python using Flask and SocketIO.

## Installation

```bash
pip install pyweboverlay
```

## Usage

Set up your directory structure like the example provided in the repository:

```
│   example.py
│
└───rloverlay
    │   rloverlay.html
    │
    └───static
            background.png
            pivot.png
```

See `example.py` and the `rloverlay/` directory for a complete working example.

<img width="584" height="124" alt="image" src="https://github.com/user-attachments/assets/a81631ee-38f7-4795-8a9e-4d5131adce98" />

## API Reference

### `pyweboverlay.init(port=5000, verbose=True)`

Initialize the pyweboverlay server.

- **port** (int): Port number for the web server (default: 5000)
- **verbose** (bool): Enable detailed logging (default: True)

### `pyweboverlay.register(overlay, name, template_file=None, static_dir=None)`

Register an overlay instance with the server.

- **overlay** (Overlay): Instance of a class extending Overlay
- **name** (str): Unique name for the overlay's namespace
- **template_file** (str, optional): Path to custom HTML template file
- **static_dir** (str, optional): Path to directory for serving static files

Returns the overlay ID.

### `pyweboverlay.update(name, data=None)`

Update an overlay with new data and emit to connected clients.

- **name** (str): The registered name of the overlay
- **data** (any): Data to pass to the overlay's update method

### Creating Custom Overlays

Extend the `Overlay` base class and implement two required methods:

```python
from pyweboverlay import Overlay

class CustomOverlay(Overlay):
    def get_data(self):
        """Return current overlay data as a dictionary."""
        return {"key": "value"}
    
    def update(self, data=None):
        """Update the overlay state with new data."""
        if data is not None:
            # Process and store the data
            pass
```

## Features

- Real-time updates using WebSocket connections
- Custom HTML templates with Jinja2 templating
- Static file serving for images, CSS, and JavaScript
- Multiple overlays on a single server
- Minimal configuration required

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/chrisrca/pyweboverlay/blob/main/LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
