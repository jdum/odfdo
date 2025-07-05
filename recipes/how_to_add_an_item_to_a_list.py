#!/usr/bin/env python
"""Minimal example of how to add an item to a list."""

import os

from odfdo import List, ListItem

_DOC_SEQUENCE = 28


def generate_list() -> List:
    """Return a small List."""
    drink_list = List(["chocolate", "coffee"])
    item = ListItem("tea")
    drink_list.append(item)

    return drink_list


def main() -> None:
    some_list = generate_list()
    test_unit(some_list)


def test_unit(some_list: List) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert str(some_list).strip() == "-  chocolate\n -  coffee\n -  tea"


if __name__ == "__main__":
    main()
