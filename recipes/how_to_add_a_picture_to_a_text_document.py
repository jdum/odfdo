from odfdo import Document, Paragraph, Frame

doc = Document("text")
body = doc.body

uri = doc.add_file("newlogo.png")
image_frame = Frame.image_frame(uri, size=("6cm", "4cm"), position=("5cm", "10cm"))

# put image frame in a paragraph:
para = Paragraph("")
para.append(image_frame)
body.append(para)

# doc.save(target='test_picture.odt', pretty=True)
