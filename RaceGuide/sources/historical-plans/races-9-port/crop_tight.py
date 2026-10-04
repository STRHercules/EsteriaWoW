"""Tight crop of the helmet/head region for a clear read of the offset."""
from pathlib import Path

from PIL import Image, ImageEnhance

SOURCE = Path(r"R:\Users\Zach\Documents\ShareX\Screenshots\2026-09\Wow_bHsZ05IgyZ.png")
TARGET = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\.agents\plans\races-9-port\debug-vulpera-tight.png")

image = Image.open(SOURCE).convert("RGB")
crop = image.crop((190, 110, 470, 430))
crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
crop = ImageEnhance.Contrast(crop).enhance(1.3)
crop = ImageEnhance.Brightness(crop).enhance(1.1)
crop.save(TARGET)
print("wrote", TARGET, crop.size)
