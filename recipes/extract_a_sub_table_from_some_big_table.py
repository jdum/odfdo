#!/usr/bin/env python
"""
Create a table of 1000 lines and 100 columns, extract a sub table of 100 lines
26 columns, save the result in a spreadsheet document.
"""
import os

from odfdo import Document, Table, Row, Cell


def suite(n):
    if n % 2 == 0:
        return n / 2
    return 3 * n + 1


if __name__ == "__main__":
    spreadsheet = Document('spreadsheet')

    # Populate the table in the spreadsheet
    body = spreadsheet.body
    table = Table("Big Table")
    body.append(table)

    lines = 1000
    cols = 100

    for line in range(lines):
        row = Row()
        values = []
        n = line
        for i in range(cols):
            values.append(n)
            n = suite(n)
        row.set_values(values)
        table.append(row)

    print("Size of Big Table :", table.size)

    # now extract 100 rows of 26 columns :
    table1 = Table("Extract 1")
    for r in range(800, 900):
        row = table.get_row(r)
        values = [row.get_value(x) for x in range(50, 76)]
        row2 = Row()
        row2.set_values(values)
        table1.append(row2)
    body.append(table1)

    print("Size of extracted table 1 :", table1.size)

    # other method
    table2 = Table("Extract 2")
    cells = table.get_cells(coord=(50, 800, 75, 899))
    table2.set_cells(coord=(2, 3), cells=cells)
    body.append(table2)

    print("Size of extracted table 2 :", table2.size)

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = os.path.join('test_output', "my_big_spreadsheet.ods")

    spreadsheet.save(target=output, pretty=True)

    expected_result = """
Size of Big Table : (100, 1000)
Size of extracted table 1 : (26, 100)
Size of extracted table 2 : (26, 100)
"""
