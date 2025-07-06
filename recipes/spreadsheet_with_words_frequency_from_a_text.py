#!/usr/bin/env python
"""Load an ODF text, store the frequency of words in a spreadsheet,
make requests on the table, by regex or value.
"""

import os
import sys
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 710
SOURCE = "collection2.odt"
DATA = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "freq"
TARGET = "frequency.ods"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def frequence_count(document: Document) -> dict[str, int]:
    """Word frequency analysis of a document."""
    print("Word frequency analysis of", Path(document.container.path).name)
    text = str(document.body)
    for char in "():;!.,[]{}#@/\\=-_+*#@`\"'":
        text = text.replace(char, " ")  # slow algorithm
    words = text.split()
    print("Nb of words:", len(words))

    frequences = {}

    for word in words:
        frequences[word] = frequences.get(word, 0) + 1

    print("Unique words found:", len(frequences))
    return frequences


def scan_document(source: Document) -> Document:
    """Return a spreadsheet containing the word frequency of the source document."""
    spreadsheet = Document("spreadsheet")
    frequences = frequence_count(source)

    # Populate the table in the spreadsheet
    body = spreadsheet.body
    body.clear()
    table = Table("Frequency Table")
    body.append(table)

    sorted_keys = sorted([(value, key) for key, value in frequences.items()])
    sorted_keys.reverse()

    # possible solution :
    # for value, key in sorted:
    #    row = Row()
    #    row.set_value(0, key)
    #    row.set_value(1, value) # Cell type is guessed.
    #    table.append_row(row)

    # another solution :
    sorted_keys = [(k, v) for (v, k) in sorted_keys]
    table.set_values(sorted_keys)

    print("Rows in the table :", len(table.rows))

    # frequency of word:
    regex_query = "^the"
    print("Words corresponding to the regex:", regex_query)
    result = table.get_rows(content=regex_query)
    for row in result:
        print(f"  word: {row.get_value(0):<20}  occurences: {row.get_value(1)}")

    # list of words of frequecy = 15
    found = []
    for word, freq in table.iter_values():
        if freq == 15:
            found.append(word)
    print("List of words of frequency 15:", ", ".join(found))
    return spreadsheet


def main() -> None:
    document = read_source_document()
    freqs = scan_document(document)
    test_unit(freqs)
    save_new(freqs, TARGET)


def test_unit(freqs: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = freqs.body.get_table(0)
    assert table.get_cell("A1").value == "the"
    assert table.get_cell("B1").value == 699
    assert table.get_cell("A50").value == "which"
    assert table.get_cell("B50").value == 23


if __name__ == "__main__":
    main()
