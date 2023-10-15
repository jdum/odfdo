from odfdo import Document, Paragraph

document = Document("text")
body = document.body
paragraph = Paragraph("Hello World")
body.append(paragraph)
