#!/usr/bin/env python
"""Change an image in many ODF files.

This recipe is suitable for the scenario where an organization
is moving from one company logo to another and needs to replace
the logo in several hundred existing documents.
"""
from hashlib import sha256
from pathlib import Path

from odfdo import Document

counter_image = 0
counter_odf = 0
counter_hit = 0

_DOC_SEQUENCE = 270
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "new_logo"
DATA = Path(__file__).parent / "data"
OLD_PRESENTATIONS = DATA / "old_presentations"
OLD_LOGO = OLD_PRESENTATIONS / "oldlogo.png"
NEW_LOGO = DATA / "newlogo.png"


def save_modified(document: Document):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    name = Path(document.container.path).name
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path)


def footprint(content: bytes) -> str:
    return sha256(content).hexdigest()


def update_document(
    path: Path,
    old_hash: str,
    new_content: bytes,
    stats: dict,
):
    stats["files"] += 1
    if not path.suffix.lower().startswith(".od"):
        return
    try:
        document = Document(path)
    except Exception:
        return

    stats["odf_files"] += 1
    document_changed = False
    for image in document.body.images:
        image_url = image.url
        if not image_url:
            continue
        try:
            image_content = document.get_part(image_url)
        except KeyError:
            print("- not found inside document:", path, end=" ")
            print("  image URL:", image_url)
            continue
        if footprint(image_content) == old_hash:
            document.set_part(image_url, new_content)
            document_changed = True
    if document_changed:
        save_modified(document)
        stats["updated_files"] += 1


def update_logos():
    old_hash = footprint(OLD_LOGO.read_bytes())

    # making the new image content :
    buffer = Document("text")
    url = buffer.add_file(str(NEW_LOGO))
    new_content = buffer.get_part(url)

    stats = {
        "files": 0,
        "odf_files": 0,
        "updated_files": 0,
    }
    for path in OLD_PRESENTATIONS.glob("**/*"):
        update_document(path, old_hash, new_content, stats)
    return stats


def main():
    stats = update_logos()
    print(f"Files: {stats['files']}")
    print(f"ODF files: {stats['odf_files']}")
    print(f"Updated files: {stats['updated_files']}")


if __name__ == "__main__":
    main()
