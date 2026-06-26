from PIL import Image
from pathlib import Path

files = [
    'images/laser.png',
    'images/sheetmetal.png',
    'images/welding.png',
    'images/machining.png',
    'images/surface.png',
    'images/inspection.png',
]

for rel in files:
    path = Path(rel)
    img = Image.open(path).convert('RGB')
    w, h = img.size
    px = img.load()

    min_x, min_y = w, h
    max_x, max_y = -1, -1

    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 8 or g > 8 or b > 8:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if max_x == -1:
        print(f'{rel}: no non-black pixels')
        continue

    bw = max_x - min_x + 1
    bh = max_y - min_y + 1
    print(f'{rel}: size=({w},{h}) nonblack=({min_x},{min_y},{max_x},{max_y}) region=({bw},{bh})')
