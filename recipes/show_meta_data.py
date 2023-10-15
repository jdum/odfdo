#!/usr/bin/env python
"""Print the metadata informations of a ODF file.
"""
import sys
from pathlib import Path

from odfdo import Document

DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    document = read_source_document()

    # Metadata are accessible through the meta part:
    meta = document.get_part("meta.xml")

    # You then get access to various getters and setters. The getters return
    # Python types and the respective setters take the same Python type as
    # a parameter.
    #
    # Here are the output of the get_xxx methods for metadata.
    # (Notice that LpOD doesn’t increment editing cycles nor statistics
    # when saving the document.
    # For the metadata using dates or durations, lpOD provides datatypes that
    # decode from and serialize back to strings.
    # Strings are always decoded as unicode, numeric values are always decoded
    # as Decimal (as they offer the best precision).

    print(f"Meta data of {document.container.path}")
    print("Title                :", meta.get_title())
    print("creator              :", meta.get_creator())
    print("creation date        :", meta.get_creation_date())
    print("modification date    :", meta.get_modification_date())
    print("initial creator      :", meta.get_initial_creator())
    print("subject              :", meta.get_subject())
    print("description          :", meta.get_description())
    print("comments             :", meta.get_comments())
    print("editing cycles       :", meta.get_editing_cycles())
    print("editing duration     :", meta.get_editing_duration())
    print("generator            :", meta.get_generator())
    print("language             :", meta.get_language())
    print("keywords             :", meta.get_keywords())
    print("statistics    ")
    if meta.get_statistic() is not None:
        for key, value in meta.get_statistic().items():
            print(f"   {key[5:]:<18}: {value}")
    if meta.get_user_defined_metadata() is not None:
        print("user defined metadata")
        for key, value in meta.get_user_defined_metadata().items():
            print(f"   {key[5:]:<18}: {value}")

    # A quick way to have all of those informations:
    print("-" * 70)
    print(document.get_formated_meta())


if __name__ == "__main__":
    main()
