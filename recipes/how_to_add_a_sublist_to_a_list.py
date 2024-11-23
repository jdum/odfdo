"""Minimal example of how to add a paragraph.
"""

from odfdo import Document, List, ListItem

_DOC_SEQUENCE = 27


def main():
    document = Document("text")
    body = document.body

    my_list = List(["chocolat", "café"])
    body.append(my_list)

    item = ListItem("thé")
    my_list.append(item)

    # A sublist is simply a list as an item of another list
    item.append(List(["thé vert", "thé rouge"]))

    print(body.serialize(True))


if __name__ == "__main__":
    main()
