from odfdo import Document, Header, Paragraph, Table

document = Document("text")
body = document.body

# Let's add another section to make our document clear:

body.append(Header(1, "Tables"))
body.append(Paragraph("A 3x3 table:"))

# Creating a table :

table = Table("Table 1", width=3, height=3)
body.append(table)
