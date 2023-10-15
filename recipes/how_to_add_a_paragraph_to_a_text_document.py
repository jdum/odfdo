from odfdo import Document, Paragraph

document = Document("text")
body = document.body

# create a new paragraph with some content :
paragraph = Paragraph("Hello World")
body.append(paragraph)
