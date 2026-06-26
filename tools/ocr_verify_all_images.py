import cv2
import pytesseract
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

files = [
    Path('images/hero.png'),
    Path('images/laser.png'),
    Path('images/sheetmetal.png'),
    Path('images/welding.png'),
    Path('images/machining.png'),
    Path('images/surface.png'),
    Path('images/inspection.png'),
    Path('images/factory.png'),
    Path('images/products.png'),
]

for path in files:
    img = cv2.imread(str(path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config='--oem 3 --psm 6')
    words = []
    for i, text in enumerate(data['text']):
        if not text or not text.strip():
            continue
        conf_raw = data['conf'][i]
        try:
            conf = float(conf_raw)
        except Exception:
            conf = -1
        if conf >= 40:
            words.append(text.strip())
    print(f'{path}: {words[:12]}')
