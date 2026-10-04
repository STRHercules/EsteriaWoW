"""Crop and upscale the head area of the user's screenshot."""
from pathlib import Path

from PIL import Image

SOURCE = Path(r"R:\Users\Zach\Documents\ShareX\Screenshots\2026-09\Wow_bHsZ05IgyZ.png")
TARGET = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\.agents\plans\races-9-port\debug-vulpera-head-zoom.png")

image = Image.open(SOURCE)
print("size:", image.size)
width, height = image.size
box = (int(width * 0.25), int(height * 0.10), int(width * 0.80), int(height * 0.60))
crop = image.crop(box)
crop = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
crop.save(TARGET)
print("wrote", TARGET, crop.size)
