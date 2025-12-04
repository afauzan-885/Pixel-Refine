import sys
import os

# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pixel_refine.app import PixelRefineApp

if __name__ == "__main__":
    PixelRefineApp().run()
