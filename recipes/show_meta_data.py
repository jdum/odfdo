#!/usr/bin/env python
"""Print the metadata informations of a ODF file.

Metadata are accessible through the meta part: meta = document.get_part("meta.xml")
or the shortcut: document.meta.

You then get access to various getters and setters. The getters return
Python types and the respective setters take the same Python type as
a parameter.
"""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 490
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def print_meta(document: Document) -> None:
    """Print the medadata of the document.

    Output of the get_xxx methods for metadata.
    Notice that odfdo doesn't increment editing cycles nor statistics
    when saving the document.
    For the metadata using dates or durations, odfdo provides datatypes that
    decode from and serialize back to strings.
    Strings are always decoded as utf-8, numeric values are decoded
    as Decimal."""

    meta = document.meta

    print(f"Meta data of {document.path}")
    print("Title                :", meta.title)
    print("creator              :", meta.creator)
    print("creation date        :", meta.creation_date)
    print("modification date    :", meta.date)
    print("initial creator      :", meta.initial_creator)
    print("subject              :", meta.subject)
    print("description          :", meta.description)
    print("editing cycles       :", meta.editing_cycles)
    print("editing duration     :", meta.editing_duration)
    print("generator            :", meta.generator)
    print("language             :", meta.language)
    print("keywords             :", meta.keyword)
    print("statistics    ")
    if meta.statistic is not None:
        for key, value in meta.statistic.items():
            print(f"   {key[5:]:<18}: {value}")
    user_defined = meta.user_defined_metadata
    if user_defined:
        print("user defined metadata")
        for key, value in user_defined.items():
            print(f"   {key[5:]:<18}: {value}")

    # A quick way to have all of those informations:
    print("-" * 70)
    print(document.get_formated_meta())


def main() -> None:
    document = read_source_document()
    print_meta(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    meta = document.meta
    assert meta.keyword.strip() == "Douglas Adams"
    assert meta.statistic["meta:page-count"] == 20


if __name__ == "__main__":
    main()
