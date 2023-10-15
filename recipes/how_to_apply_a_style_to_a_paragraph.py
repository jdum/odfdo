from odfdo import Document, Paragraph

document = Document("text")
body = document.body

# we knwo we have a style of name "highlight" :
body.append(Paragraph("Highlighting the word", style="highlight"))
