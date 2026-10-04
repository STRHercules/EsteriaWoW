"""Zoom the new Vulpera screenshot."""
from pathlib import Path

from PIL import Image, ImageEnhance

SOURCE = Path(r"C:\Users\Zach\AppData\Local\Temp\codex-clipboard-0e25db60-deb1-4d76-9a9a-e1665d7e1734.png")
TARGET = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\.agents\plans\races-9-port\debug-vulpera-helm-2.png")

image = Image.open(SOURCE).convert("RGB")
print("size:", image.size)
width, height = image.size
crop = image.crop((int(width * 0.30), 0, width, int(height * 0.75)))
crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
crop = ImageEnhance.Contrast(crop).enhance(1.25)
crop = ImageEnhance.Brightness(crop).enhance(1.15)
crop.save(TARGET)
print("wrote", TARGET, crop.size)
