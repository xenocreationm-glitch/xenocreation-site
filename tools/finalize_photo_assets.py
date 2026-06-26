from pathlib import Path

import cv2
from PIL import Image


def crop_remove_bottom_band(path: Path, keep_height: int, restore_size: tuple[int, int] | None = None) -> None:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    keep_height = min(max(1, keep_height), height)
    cropped = image.crop((0, 0, width, keep_height))

    if restore_size is not None:
        cropped = cropped.resize(restore_size, Image.Resampling.LANCZOS)

    cropped.save(path, optimize=True)
    print(f"updated {path} -> {cropped.size}")


def inpaint_hero_logo(path: Path) -> None:
    image = cv2.imread(str(path))
    if image is None:
        print(f"skip {path}")
        return

    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask[:, :] = 0

    # Logo/marking areas on the machine head in current hero image (778x447).
    cv2.rectangle(mask, (480, 58), (612, 146), 255, -1)
    cv2.rectangle(mask, (486, 126), (560, 154), 255, -1)

    cleaned = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(str(path), cleaned)
    print(f"updated {path} -> logo removed")


ROOT = Path(".")

# Remove visible UI/label bands while preserving the photo composition.
crop_remove_bottom_band(ROOT / "images" / "factory.png", keep_height=760)
crop_remove_bottom_band(ROOT / "images" / "products.png", keep_height=172)

# Service images were previously normalized to 1281x520; keep same size after cleaning.
crop_remove_bottom_band(ROOT / "images" / "surface.png", keep_height=338, restore_size=(1281, 520))
crop_remove_bottom_band(ROOT / "images" / "inspection.png", keep_height=338, restore_size=(1281, 520))

# Remove small logo marking from hero machine head.
inpaint_hero_logo(ROOT / "images" / "hero.png")
