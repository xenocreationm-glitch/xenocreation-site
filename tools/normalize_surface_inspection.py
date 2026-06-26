from PIL import Image
from pathlib import Path

TARGETS = [
    Path('images/surface.png'),
    Path('images/inspection.png'),
]

TARGET_SIZE = (1281, 520)
THRESHOLD = 8

for path in TARGETS:
    img = Image.open(path).convert('RGB')
    w, h = img.size
    px = img.load()

    min_x, min_y = w, h
    max_x, max_y = -1, -1

    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > THRESHOLD or g > THRESHOLD or b > THRESHOLD:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if max_x == -1:
        print(f'skip {path}: no non-black region')
        continue

    cropped = img.crop((min_x, min_y, max_x + 1, max_y + 1))
    resized = cropped.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    resized.save(path, optimize=True)
    print(f'normalized {path} from {img.size} region=({max_x - min_x + 1},{max_y - min_y + 1}) -> {TARGET_SIZE}')
