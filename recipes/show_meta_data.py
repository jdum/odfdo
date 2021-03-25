#!/usr/bin/env python
"""
Print the metadata informations of a ODF file.
"""
import sys

from odfdo import Document


def get_default_doc():
    # ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
    return "collection2.odt"


if __name__ == "__main__":
    try:
        source = sys.argv[1]
    except IndexError:
        source = get_default_doc()

    # To illustrate metadata introspection, let’s open an existing document:
    document = Document(source)

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

    print("Meta data of %s" % source)
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
            print("   %-18s: %s" % (key[5:], value))
    if meta.get_user_defined_metadata() is not None:
        print("user defined metadata")
        for key, value in meta.get_user_defined_metadata().items():
            print("   %-18s: %s" % (key, value))

    # A quick way to have all of those informations:
    print("-" * 70)
    print(document.get_formated_meta())

    expected_result = """
Meta data of collection2.odt
Title                : The Hitchhiker's Guide to the Galaxy
creator              : None
creation date        : None
modification date    : 2010-12-13 17:29:31
initial creator      : None
subject              : Wikipedia article about The Hitchhiker's Guide to the Galaxy
description          : This file comes from a ODF export of  Wikipedia web site.

The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created
by English writer, dramatist, and musician Douglas Adams. comments : This file
comes from a ODF export of Wikipedia web site.

The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created
by English writer, dramatist, and musician Douglas Adams.
editing cycles : 7
editing duration : 0:16:19
generator : LibreOffice/3.3$Unix OpenOffice.org_project/330m9$Build-1
language : en
keywords : Douglas Adams
statistics
   word-count        : 8886
   image-count       : 0
   object-count      : 0
   page-count        : 20
   character-count   : 53645
   paragraph-count   : 197
   table-count       : 0
user defined metadata
   Rights            : GFDL
----------------------------------------------------------------------
Title: The Hitchhiker's Guide to the Galaxy
Subject: Wikipedia article about The Hitchhiker's Guide to the Galaxy
Language: en
Modification date: 2010-12-13 17:29:31
Keyword: Douglas Adams
Editing duration: 0:16:19
Editing cycles: 7
Generator: LibreOffice/3.3$Unix OpenOffice.org_project/330m9$Build-1
Statistic:
  - Word count: 8886
  - Image count: 0
  - Object count: 0
  - Page count: 20
  - Character count: 53645
  - Paragraph count: 197
  - Table count: 0
User defined metadata:
  - Rights: GFDL
Description: This file comes from a ODF export of  Wikipedia web site.

The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created
by English writer, dramatist, and musician Douglas Adams.

"""
