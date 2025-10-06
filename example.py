import time
import pyweboverlay
from pyweboverlay.core import Overlay

class SampleOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.sample = 0

    def get_data(self):
        """Return current sample data."""
        return {"samples": self.sample}

    def update(self, data=None):
        """Update the samples count."""
        if data is not None:
            self.sample = data

if __name__ == "__main__":
    pyweboverlay.init(port=5001, verbose=False)
    overlay_instance = SampleOverlay()
    pyweboverlay.register(
        overlay_instance,
        name="sample",
        template_file="sample/sample.html",
        static_dir="sample/static",
    )
    print(f"Visit http://localhost:5001/sample to see the overlay")

    samples_var = 0
    try:
        while True:
            samples_var += 1
            pyweboverlay.update("sample", samples_var)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user")