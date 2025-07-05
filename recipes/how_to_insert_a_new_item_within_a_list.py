#!/usr/bin/env python
"""Minimal example of how to insert a new item within a list."""

import os

from odfdo import List

_DOC_SEQUENCE = 29


def generate_list() -> List:
    """Return a List with inserted items."""
    drink_list = List(["chocolate", "coffee"])

    # insert as second item:
    drink_list.insert_item("tea", position=1)

    # insert it before another item:
    coffee = drink_list.get_item(content="coffee")
    drink_list.insert_item("green tea", before=coffee)

    # Or after:
    drink_list.insert_item("black tea", after=coffee)

    print(str(drink_list))
    return drink_list


def main() -> None:
    some_list = generate_list()
    test_unit(some_list)


def test_unit(some_list: List) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert str(some_list).strip() == (
        "-  chocolate\n -  tea\n -  green tea\n -  coffee\n -  black tea"
    )


if __name__ == "__main__":
    main()
