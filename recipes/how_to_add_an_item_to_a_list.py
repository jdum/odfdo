"""Minimal example of how to add an item to a list.
"""

from odfdo import List, ListItem

_DOC_SEQUENCE = 28


def main():
    a_list = List(["chocolat", "café"])
    item = ListItem("thé")
    a_list.append(item)


if __name__ == "__main__":
    main()
