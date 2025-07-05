#!/usr/bin/env python
"""Create a basic text document with headers and praragraphs."""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 10
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_text"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def create_basic_document() -> Document:
    """Generate a basic text document."""
    document = Document("text")
    body = document.body
    body.clear()
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


def main() -> None:
    document = create_basic_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    text = str(document.body.get_paragraph(position=1))
    assert text.startswith("Cette île est de forme triangulaire")


if __name__ == "__main__":
    main()
