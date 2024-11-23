#!/usr/bin/env python
"""Analyse a list of files and directory (recurse), open all ODF documents
and copy pictures from documents in a directory.
"""
import sys
import time
from hashlib import sha256
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 530
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "collected_pics"
DATA = Path(__file__).parent / "data"

# encoding = "UTF8"
known_images = set()
counter_image = 0
counter_odf = 0
counter_outside = 0


def store_image(path, name, content):
    """Image new name is "odffile_imagename"."""
    global counter_image

    base = path.name.replace(".", "_")
    cpt = 1
    if not OUTPUT_DIR.is_dir():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / f"{base}_{cpt}_{name}"
    while target.exists():
        cpt += 1
        target = OUTPUT_DIR / f"{base}_{cpt}_{name}"
    target.write_bytes(content)
    counter_image += 1


def parse_odf_pics(path: Path):
    """Using odfdo for:
    - open possible ODF document: Document (including URI)
    - find images inside the document: get_image_list, get_attribute
    """
    if not path.suffix.lower().startswith(".od"):
        return
    try:
        document = Document(path)
    except Exception:
        return

    global counter_odf
    global counter_outside

    counter_odf += 1
    for image in document.body.images:
        image_url = image.url
        if not image_url:
            continue
        try:
            image_content = document.get_part(image_url)
        except KeyError:
            print("- not found inside document:", path)
            print("  image URL:", image_url)
            counter_outside += 1
            continue
        image_name = image_url.split("/")[-1]
        if not known_pic(image_content):
            store_image(path, image_name, image_content)


def known_pic(content) -> bool:
    """Remember already seen images by sha256 footprint."""
    footprint = sha256(content).digest()
    if footprint in known_images:
        return True
    known_images.add(footprint)
    return False


def analyse_document(source):
    for path in source.glob("**/*"):
        if path.is_file():
            parse_odf_pics(path)


def main():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA

    t0 = time.time()
    analyse_document(Path(source))
    elapsed = time.time() - t0
    print(
        f"{counter_image} images copied ({counter_outside} not found) from "
        f"{counter_odf} ODF files to {OUTPUT_DIR} in {elapsed:.2f}sec."
    )


if __name__ == "__main__":
    main()
