# Let's add another section to make our document clear:
# Annotations are notes that don’t appear in the document but typically on a
# side bar in a desktop application. So they are not printed.
from odfdo import Document, Paragraph, Header

document = Document('text')
body = document.body

body.append(Header(1, "Annotations"))
paragraph = Paragraph("A paragraph with an annotation in the middle.")
body.append(paragraph)

# Annotations are inserted like notes but they are simpler:

paragraph.insert_annotation(
    after="annotation", body="It's so easy!", creator="Luis")

# Annotation arguments are quite different:
# after   =>  The word after what the annotation is inserted.
# body    =>  The annotation itself, at the end of the page.
# creator =>  The author of the annotation.
# date    =>  A datetime value, by default datetime.now().
