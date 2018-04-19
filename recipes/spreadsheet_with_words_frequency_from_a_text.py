#!/usr/bin/env python
"""
Load an ODF text, store the frequency of words in a spreadsheet, make requests
on the table, by regex or value.
"""
import os
import sys

from odfdo import Document, Table, Row


def get_default_doc():
    return "collection2.odt"


if __name__ == "__main__":
    try:
        source = sys.argv[1]
    except IndexError:
        source = get_default_doc()

    document_source = Document(source)
    spreadsheet = Document('spreadsheet')

    print("Word frequency analysis of", source)
    text = document_source.body.text_recursive
    for c in "():;!.,[]{}#@/\\=-_+*#@`\"'":
        text = text.replace(c, ' ')  # slow algorithm
    words = text.split()
    print("nb of words:", len(words))

    frequences = {}

    for word in words:
        frequences[word] = frequences.get(word, 0) + 1

    print("unique words found:", len(frequences))

    # Populate the table in the spreadsheet
    body = spreadsheet.body
    table = Table("Frequency Table")
    body.append(table)

    sorted = [(value, key) for key, value in frequences.items()]
    sorted.sort()
    sorted.reverse()

    # one solution :

    #for value, key in sorted:
    #    row = Row()
    #    row.set_value(0, key)
    #    row.set_value(1, value) # Cell type is guessed.
    #    table.append_row(row)

    # another solution :
    sorted = [(k, v) for (v, k) in sorted]
    table.set_values(sorted)

    print("rows in the table :", len(table.get_rows()))

    # frequency of word:
    regex_query = "^the"
    print("Words corresponding to the regex:", regex_query)
    result = table.get_rows(content=regex_query)
    for row in result:
        print("word: %-20s  occurences: %s" % (row.get_value(0),
                                               row.get_value(1)))

    # list of words of frequecy = 15
    found = []
    for word, freq in table.iter_values():
        if freq == 15:
            found.append(word)
    print("list of words of frequency 15:", ", ".join(found))

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = os.path.join('test_output', "my_frequency_spreadsheet.ods")

    spreadsheet.save(target=output, pretty=True)

    expected_result = """
Word frequency analysis of collection2.odt
nb of words: 9128
unique words found: 2337
rows in the table : 2337
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
list of words of frequency 15: two, they, release, one, its, his, film,
episodes, but, adaptation, UK, Radio, J, 0

"""
