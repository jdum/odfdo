#!/usr/bin/env python
"""Add not printable annotations to a document.

Annotations are notes that do not appear in the document but typically
on a side bar in a desktop application. So they are not printed.
"""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 110
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "annotated"
TARGET = "annotated_document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def base_document() -> Document:
    """Generate a basic document."""
    document = Document("text")
    body = document.body

    body.append(Header(1, "De la Guerre des Gaules - Livre V"))
    body.append(Header(2, "Préparatifs d'expédition en Bretagne"))
    body.append(
        Paragraph(
            "Sous le consulat de Lucius Domitius et d'Appius Claudius, "
            "César, quittant les quartiers d'hiver pour aller en Italie, "
            "comme il avait coutume de le faire chaque année, ordonne aux "
            "lieutenants qu'il laissait à la tête des légions de construire, "
            "pendant l'hiver, le plus de vaisseaux qu'il serait possible, "
            "et de réparer les anciens."
        )
    )
    body.append(Header(2, "La Bretagne"))
    body.append(
        Paragraph(
            "Cette île est de forme triangulaire ; l'un des côtés regarde "
            "la Gaule. Des deux angles de ce côté, l'un est au levant, "
            "vers le pays de Cantium, où abordent presque tous les vaisseaux "
            "gaulois ; l'autre, plus bas, est au midi. La longueur de ce côté "
            "est d'environ cinq cent mille pas. "
        )
    )
    return document


def insert_annotation(document: Document) -> None:
    """Insert a not printable annotation in a document."""
    body = document.body
    paragraph = body.get_paragraph(content="consulat")
    # Annotations are inserted like notes but they are simpler:
    # Annotation arguments:
    # after   =>  The word after what the annotation is inserted.
    # body    =>  The annotation itself, at the end of the page.
    # creator =>  The author of the annotation.
    # date    =>  A datetime value, by default datetime.now().
    paragraph.insert_annotation(
        after="Domitius",
        body="Talking about Lucius Domitius",
        creator="Luis",
    )


def main() -> None:
    document = base_document()
    insert_annotation(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.get_annotations(creator="Luis")) == 1


if __name__ == "__main__":
    main()
