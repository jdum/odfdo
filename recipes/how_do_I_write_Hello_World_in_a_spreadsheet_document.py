from odfdo import Document, Table

document = Document("spreadsheet")
body = document.body

table = Table("Empty Table")
table.set_value("A1", "Hello World")
body.append(table)
