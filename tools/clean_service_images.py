import cv2
import numpy as np
import pytesseract
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

files = [
    Path('images/laser.png'),
    Path('images/sheetmetal.png'),
    Path('images/welding.png'),
    Path('images/machining.png'),
    Path('images/surface.png'),
    Path('images/inspection.png'),
]

for path in files:
    img = cv2.imread(str(path))
    if img is None:
        print(f'skip {path}')
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(gray.shape, dtype=np.uint8)

    for psm in (6, 11, 13):
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=f'--oem 3 --psm {psm}')
        for i, text in enumerate(data['text']):
            if not text or not text.strip():
                continue
            conf = int(data['conf'][i]) if data['conf'][i] != '' else 0
            x = int(data['left'][i])
            y = int(data['top'][i])
            w = int(data['width'][i])
            h = int(data['height'][i])
            if conf > 30 and w * h > 180:
                x0 = max(0, x - 10)
                y0 = max(0, y - 8)
                x1 = min(gray.shape[1], x + w + 10)
                y1 = min(gray.shape[0], y + h + 8)
                cv2.rectangle(mask, (x0, y0), (x1, y1), 255, -1)

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    gray_blur = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray_blur, 235, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 80 < w * h < 40000:
            pad = 6
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(gray.shape[1], x + w + pad)
            y1 = min(gray.shape[0], y + h + pad)
            cv2.rectangle(mask, (x0, y0), (x1, y1), 255, -1)

    # keep a soft border around the top/bottom to avoid harsh edge artifacts
    if np.count_nonzero(mask) > 0:
        out = cv2.inpaint(img, mask, 3, flags=cv2.INPAINT_TELEA)
        cv2.imwrite(str(path), out)
        print(f'processed {path}')
    else:
        print(f'no mask {path}')
