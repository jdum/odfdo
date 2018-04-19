#!/usr/bin/env python
"""
Create a spreadsheet with one table.
"""
import os

from odfdo import Document, Table

if __name__ == "__main__":

    # creating an empty spreadsheet document:
    document = Document('spreadsheet')

    # Each sheet of a spreadsheet is a table:
    # setting drom the beginning width (columns) and height (rows)
    # is not mandatory, but a good practice, since odfdo don't check
    # actual existence of cells
    body = document.body
    table = Table("First Table", width=20, height=3)
    body.append(table)

    # A table contains rows, we can append some more.
    for r in range(2):
        table.append_row()
    print("rows in the table (3+2):", len(table.get_rows()))

    #  A row contains cells
    for row in table.get_rows():
        print("row, nb of cells ", row.y, len(row.get_cells()))

    last_row = table.get_row(-1)
    print("nb of cells of the last row:", len(last_row.get_cells()))

    # cell can have different kind of values
    for r in range(3):
        for c in range(10):
            table.set_value((c, r), "cell %s %s" % (c, r))
    for r in range(3, 5):
        for c in range(10):
            table.set_value((c, r), c * 100 + r)

    # Before saving the document,  we can strip the unused colums:
    print("table size:", table.size)
    table.rstrip()
    print("table size after strip:", table.size)
    print("nb of cells of the last row:", len(table.get_row(-1).get_cells()))
    print("Content of the table:")
    print(table.to_csv())

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = os.path.join('test_output', "my_basic_spreadsheet.ods")

    document.save(target=output, pretty=True)
