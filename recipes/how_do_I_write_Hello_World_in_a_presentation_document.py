# I want to write "Hello World" in the middle of the first page.

from odfdo import Document, Frame, DrawPage

document = Document("presentation")
body = document.body

page = DrawPage("page1", name="Page 1")
body.append(page)
text_frame = Frame(
    ["Hello", "World"],
    size=("7cm", "5cm"),
    position=("11cm", "8cm"),
    style="colored",
    text_style="big",
)
