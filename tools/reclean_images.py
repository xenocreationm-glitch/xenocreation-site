import cv2
import numpy as np
import pytesseract
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

TARGETS = [
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


def add_box(mask: np.ndarray, x: int, y: int, w: int, h: int, pad: int = 12) -> None:
    h0, w0 = mask.shape[:2]
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(w0, x + w + pad)
    y2 = min(h0, y + h + pad)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)


def detect_text_boxes(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes: list[tuple[int, int, int, int]] = []

    for psm in (6, 11, 13):
        data = pytesseract.image_to_data(
            gray,
            output_type=pytesseract.Output.DICT,
            config=f'--oem 3 --psm {psm}',
        )
        for i, text in enumerate(data['text']):
            if not text or not text.strip():
                continue
            conf_text = data['conf'][i]
            try:
                conf = float(conf_text)
            except Exception:
                conf = -1
            if conf < 25:
                continue
            x = int(data['left'][i])
            y = int(data['top'][i])
            w = int(data['width'][i])
            h = int(data['height'][i])
            if w * h < 120:
                continue
            boxes.append((x, y, w, h))

    # catch thin white overlays that OCR may miss
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bright = cv2.threshold(blur, 232, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if 60 < area < 50000:
            boxes.append((x, y, w, h))

    # de-duplicate overlapping boxes loosely
    deduped: list[tuple[int, int, int, int]] = []
    for box in boxes:
        x, y, w, h = box
        keep = True
        for ox, oy, ow, oh in deduped:
            ix1 = max(x, ox)
            iy1 = max(y, oy)
            ix2 = min(x + w, ox + ow)
            iy2 = min(y + h, oy + oh)
            if ix2 > ix1 and iy2 > iy1:
                inter = (ix2 - ix1) * (iy2 - iy1)
                if inter / float(min(w * h, ow * oh)) > 0.4:
                    keep = False
                    break
        if keep:
            deduped.append(box)
    return deduped


for path in TARGETS:
    image = cv2.imread(str(path))
    if image is None:
        print(f'skip {path}')
        continue

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    boxes = detect_text_boxes(image)
    for x, y, w, h in boxes:
        add_box(mask, x, y, w, h, pad=14)

    # Slightly enlarge small fragments to remove leftover punctuation / characters.
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    if np.count_nonzero(mask) == 0:
        print(f'no text found {path}')
        continue

    cleaned = cv2.inpaint(image, mask, 3, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(str(path), cleaned)
    print(f'processed {path} boxes={len(boxes)}')
