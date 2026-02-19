import mss
import mss.tools
from PIL import Image

def capture():
    with mss.mss() as sct:
        filename = sct.shot(mon=-1, output='desktop_shot.png')
        print(f"Screenshot saved to {filename}")

if __name__ == "__main__":
    capture()
