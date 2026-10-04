"""Prepare approved personal photos for the public website.

The generated WebP files are resized for the page and intentionally omit EXIF
metadata. Source photos should remain outside the public repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"


def open_rgb(path: Path) -> Image.Image:
    with Image.open(path) as source:
        corrected = ImageOps.exif_transpose(source)
        return corrected.convert("RGB")


def save_portrait(source: Path) -> None:
    image = open_rgb(source)
    portrait = ImageOps.fit(
        image,
        (800, 1000),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.43),
    )
    portrait.save(IMAGES / "portrait.webp", "WEBP", quality=88, method=6)


def save_life_photo(
    source: Path,
    filename: str,
    width: int,
    crop_bottom_ratio: float = 0,
) -> None:
    image = open_rgb(source)
    if crop_bottom_ratio:
        image = image.crop((0, 0, image.width, round(image.height * (1 - crop_bottom_ratio))))
    if image.width > width:
        height = round(image.height * width / image.width)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    life_dir = IMAGES / "life"
    life_dir.mkdir(parents=True, exist_ok=True)
    image.save(life_dir / filename, "WEBP", quality=84, method=6)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portrait", type=Path, required=True)
    parser.add_argument("--campus", type=Path, required=True)
    parser.add_argument("--travel", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    IMAGES.mkdir(parents=True, exist_ok=True)
    save_portrait(args.portrait)
    save_life_photo(
        args.campus,
        "hkust-clear-water-bay.webp",
        1600,
        crop_bottom_ratio=0.1,
    )
    save_life_photo(args.travel, "travel-portrait.webp", 1200)
    print("Prepared public portrait and two life photographs.")


if __name__ == "__main__":
    main()
