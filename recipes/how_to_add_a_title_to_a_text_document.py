from odfdo import Document, Header

document = Document("text")
body = document.body

title1 = Header(1, "The Title")
body.append(title1)
