import time
import random
import pyweboverlay
from pyweboverlay import Overlay

def abbreviate_number(number):
    """Convert a number to a string with M, B, or T abbreviation."""
    try:
        num = int(number)
    except (ValueError, TypeError):
        return str(number)

    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.1f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    else:
        return f"{num:,}"

class RLOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.samples = f"{0}"
        self.hour = f"{0}"

    def get_data(self):
        """Return current samples and hour data."""
        return {"samples": self.samples, "hour": self.hour}

    def update(self, data=None):
        """Update the samples and/or hour data independently."""
        if data is not None:
            if not isinstance(data, dict):
                raise ValueError("Data must be a dictionary")
            if "samples" in data:
                self.samples = str(data["samples"])
            if "hour" in data:
                self.hour = str(data["hour"])

if __name__ == "__main__":
    # Initialize pyweboverlay and register custom overlay
    pyweboverlay.init(port=5001, verbose=False)
    pyweboverlay.register(
        RLOverlay(),
        name="rloverlay",
        template_file="rloverlay/rloverlay.html",
        static_dir="rloverlay/static",
    )

    print(f"Visit http://localhost:5001/rloverlay to see the overlay")

    # In your code you can update data to be sent to the overlay
    samples_var = 0
    hours_var = 0
    try:
        while True:
            samples_var += random.randint(10000, 10000000)
            pyweboverlay.update("rloverlay", {"samples": abbreviate_number(samples_var)})
            time.sleep(1)
            
            if samples_var % 5 == 0:
                hours_var += 1
                pyweboverlay.update("rloverlay", {"hour": f"{hours_var}"})
            
    except KeyboardInterrupt:
        print("Stopped by user")