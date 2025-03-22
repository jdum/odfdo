#!/usr/bin/env python
"""Idea comming from issue #49:
Deleting content from one point to another in a .odt document.
"""

import os
from pathlib import Path

from odfdo import Document, Element, Header, Paragraph

_DOC_SEQUENCE = 400
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "delete_content"
TARGET_INITIAL = "document_initial.odt"
TARGET_FINAL = "document_final.odt"


class KeepingState:
    def __init__(self, initial: str):
        self.step = initial


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def create_base_document():
    document = Document("text")
    body = document.body
    body.clear()
    body.append(Header(1, "Some title"))
    body.append(Header(2, "part A"))
    body.append(
        Paragraph(
            "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed non risus."
        )
    )
    body.append(
        Paragraph(
            "Suspendisse lectus tortor, dignissim sit amet, adipiscing "
            "nec, ultricies sed, dolor. Cras elementum ultrices diam. "
            "Maecenas ligula massa, varius a, semper congue, euismod non, mi."
        )
    )
    body.append(Header(2, "part B"))
    body.append(
        Paragraph(
            "Proin porttitor, orci nec nonummy molestie, enim est eleifend "
            "mi, non fermentum diam nisl sit amet erat. Duis semper. "
            "Duis arcu massa, scelerisque vitae, consequat in, pretium a, "
            "enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor."
        )
    )
    body.append(
        Paragraph(
            "Cras vestibulum bibendum augue. Praesent egestas leo in pede. "
            "Praesent blandit odio eu enim. Pellentesque sed dui ut augue "
            "blandit sodales. Vestibulum ante ipsum primis in faucibus orci "
            "luctus et ultrices posuere cubilia Curae; Aliquam nibh."
        )
    )

    body.append(Header(2, "part C"))
    body.append(
        Paragraph(
            "Mauris ac mauris sed pede pellentesque fermentum. "
            "Maecenas adipiscing ante non diam sodales hendrerit. Ut "
            "velit mauris, egestas sed, gravida nec, ornare ut, mi."
        )
    )
    body.append(
        Paragraph(
            "Aenean ut orci vel massa suscipit pulvinar. Nulla sollicitudin. "
            "Fusce varius, ligula non tempus aliquam, nunc turpis "
            "ullamcorper nibh, in tempus sapien eros vitae ligula. "
            "Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur "
            "aliquet pellentesque diam. Integer quis metus vitae elit "
            "lobortis egestas."
        )
    )
    body.append(Header(2, "part D"))
    body.append(
        Paragraph(
            "Morbi vel erat non mauris convallis vehicula. Nulla et sapien. "
            "Integer tortor tellus, aliquam faucibus, convallis id, congue "
            "eu, quam. Mauris ullamcorper felis vitae erat."
            "Proin feugiat, augue non elementum posuere, metus purus "
            "iaculis lectus, et tristique ligula justo vitae magna. Aliquam "
            "convallis sollicitudin purus."
        )
    )
    body.append(
        Paragraph(
            "Praesent aliquam, enim at fermentum mollis, ligula massa "
            "adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce "
            "vulputate sem at sapien. Vivamus leo. Aliquam euismod "
            "libero eu enim. Nulla nec felis sed leo placerat imperdiet."
        )
    )
    body.append(
        Paragraph(
            "Aenean suscipit nulla in justo. Suspendisse cursus rutrum augue. "
            "Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel "
            "rhoncus faucibus, felis magna fermentum augue, et ultricies "
            "lacus lorem varius purus. Curabitur eu amet."
        )
    )
    return document


def keep_element(state: KeepingState, elem: Element) -> bool:
    # keep everythin until "part B"
    if state.step == "before":
        if isinstance(elem, Header) and "part B" in str(elem):
            state.step = "deleting"
    # delete everythin until paragraph strating with "Aenean"
    if state.step == "deleting":
        if isinstance(elem, Paragraph) and str(elem).startswith("Aenean"):
            state.step = "after"
    return state.step != "deleting"


def main():
    document = create_base_document()
    save_new(document, TARGET_INITIAL)
    # Removing part B and half the part C
    state = KeepingState("before")
    keep_list = []
    for elem in document.body.children:
        if keep_element(state, elem):
            keep_list.append(elem)
    document.body.clear()
    document.body.extend(keep_list)
    save_new(document, TARGET_FINAL)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    text0 = str(document.body.get_paragraph(position=0))
    print(text0)
    assert text0.startswith("Lorem")
    text1 = str(document.body.get_paragraph(position=3))
    print(text1)
    assert text1.startswith("Morbi")


if __name__ == "__main__":
    main()
