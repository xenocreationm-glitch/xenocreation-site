from pathlib import Path
from PIL import Image

# Keep the actual photo area only. The HTML/CSS now supplies the text overlays.
CROP_RULES = {
    'images/hero.png': (620, 0, 1398, 447),
    'images/laser.png': (0, 0, 1281, 520),
    'images/sheetmetal.png': (0, 0, 1281, 520),
    'images/welding.png': (0, 0, 1281, 520),
    'images/machining.png': (0, 0, 1281, 520),
    'images/surface.png': (0, 0, 1281, 520),
    'images/inspection.png': (0, 0, 1281, 520),
}

for rel_path, box in CROP_RULES.items():
    path = Path(rel_path)
    image = Image.open(path)
    cropped = image.crop(box)
    cropped.save(path)
    print(f'cropped {rel_path} -> {cropped.size}')
