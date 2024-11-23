"""Minimal example of how to insert a new item within a list.
"""

from odfdo import List

_DOC_SEQUENCE = 28


def main():

    a_list = List(["chocolat", "café"])

    # In case your forgot to insert an important item:
    a_list.insert_item("Chicorée", position=1)

    # Or you can insert it before another item:
    cafe = a_list.get_item(content="café")
    a_list.insert_item("Chicorée", before=cafe)

    # Or after:
    a_list.insert_item("Chicorée", after=cafe)


if __name__ == "__main__":
    main()
