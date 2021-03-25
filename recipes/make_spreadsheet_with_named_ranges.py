#!/usr/bin/env python
"""
Create a spreadsheet with two tables, using some named ranges.
"""
import os

from odfdo import Document, Table

if __name__ == "__main__":
    document = Document("spreadsheet")
    body = document.body
    table = Table("First Table")
    body.append(table)
    # populate the table :
    for i in range(10):
        table.set_value((1, i), (i + 1) ** 2)
    table.set_value("A11", "Total:")

    # lets define a named range for the 10 values :
    crange = "B1:B10"
    name = "squares_values"
    table_name = table.name
    table.set_named_range(name, crange, table_name)

    # we can define a single cell range, using notation "B11" or (1, 10) :
    table.set_named_range("total", (1, 10), table_name)

    # get named range values :
    values = table.get_named_range("squares_values").get_values(flat=True)

    # set named range value :
    result = sum(values)
    table.get_named_range("total").set_value(result)

    # lets use the named ranges from a second table :
    table2 = Table("Second Table")
    body.append(table2)

    named_range1 = table2.get_named_range("total")
    table2.set_value("A1", "name:")
    table2.set_value("B1", named_range1.name)
    table2.set_value("A2", "range:")
    table2.set_value("B2", str(named_range1.crange))
    table2.set_value("A3", "from table:")
    table2.set_value("B3", named_range1.table_name)
    table2.set_value("A4", "content:")
    table2.set_value("B4", named_range1.get_value())

    named_range2 = table2.get_named_range("squares_values")
    table2.set_value("D1", "name:")
    table2.set_value("E1", named_range2.name)
    table2.set_value("D2", "range:")
    table2.set_value("E2", str(named_range2.crange))
    table2.set_value("D3", "from table:")
    table2.set_value("E3", named_range2.table_name)
    table2.set_value("D4", "content:")
    # using "E4:4" notaion is a little hack for the area starting at E4 on row 4
    table2.set_values(values=[named_range2.get_values(flat=True)], coord="E4:4")

    print("Content of the table1:")
    print(table.name)
    print(table.to_csv())
    print(table2.name)
    print(table2.to_csv())

    # of course named ranges are stored in the document :
    if not os.path.exists("test_output"):
        os.mkdir("test_output")
    output = os.path.join("test_output", "my_spreadsheet_with_named_range.ods")
    document.save(target=output, pretty=True)
