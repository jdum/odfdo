#!/usr/bin/env python
"""Load an ODF text, store the frequency of words in a spreadsheet,
make requests on the table, by regex or value.
"""
import sys
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 710
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "freq"
SOURCE = "collection2.odt"
DATA = Path(__file__).parent / "data"
TARGET = "frequency.ods"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    document = generate_document()
    save_new(document, TARGET)
    _expected_result = """
    Word frequency analysis of collection2.odt
    Nb of words: 9128
    Unique words found: 2337
    Rows in the table : 2337
    Words corresponding to the regex: ^the
      word: the                   occurences: 644
      word: they                  occurences: 15
      word: their                 occurences: 11
      word: then                  occurences: 10
      word: there                 occurences: 7
      word: these                 occurences: 4
      word: them                  occurences: 4
      word: themselves            occurences: 2
      word: theme                 occurences: 2
      word: themed                occurences: 1
      word: theatrical            occurences: 1
    List of words of frequency 15: two, they, release, one, its, his, film,
    episodes, but, adaptation, UK, Radio, J, 0
"""


def frequence_count(document):
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


def generate_document():
    document_source = read_source_document()
    spreadsheet = Document("spreadsheet")

    frequences = frequence_count(document_source)

    # Populate the table in the spreadsheet
    body = spreadsheet.body
    body.clear()
    table = Table("Frequency Table")
    body.append(table)

    sorted_keys = reversed([(value, key) for key, value in frequences.items()])

    # one solution :

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


if __name__ == "__main__":
    main()
