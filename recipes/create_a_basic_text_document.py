#!/usr/bin/env python

import os

# Some text
txt_1 = "De la Guerre des Gaules - Livre V"
txt_a1 = "Préparatifs d'expédition en Bretagne"
txt_a2 = (
    "Sous le consulat de Lucius Domitius et d'Appius Claudius, "
    "César, quittant les quartiers d'hiver pour aller en Italie, "
    "comme il avait coutume de le faire chaque année, ordonne aux "
    "lieutenants qu'il laissait à la tête des légions de construire, "
    "pendant l'hiver, le plus de vaisseaux qu'il serait possible, "
    "et de réparer les anciens."
)
txt_b1 = "La Bretagne"
txt_b2 = (
    "Cette île est de forme triangulaire ; l'un des côtés regarde "
    "la Gaule. Des deux angles de ce côté, l'un est au levant, "
    "vers le pays de Cantium, où abordent presque tous les vaisseaux "
    "gaulois ; l'autre, plus bas, est au midi. La longueur de ce côté "
    "est d'environ cinq cent mille pas. "
)

# 0 - Import from odfdo
from odfdo import Document, Header, Paragraph

# 1 - Create the document
my_document = Document("text")
# Now document is an empty text document issued from a template. It’s a
# bit like creating a new text document in your office application,
# except odfdo templates don’t create a default paragraph.

# 2 - Adding Content
# Contents go into the body
body = my_document.body
# Now we have a context to attach new elements to. In a text document, we
# generally want to write paragraphs, lists, headings, and a table of
# content to show the document hierarchy at first.

# 2.1 - Adding Main Title
# Titles are organised by level, starting from level 1.
# So let’s add the main title of our document:
title1 = Header(1, txt_1)
body.append(title1)

# 2.2 - Adding more Titles and Paragraphs
# title of second level:
title = Header(2, txt_a1)
body.append(title)

# Adding a basic Paragraph of plain text
paragraph = Paragraph(txt_a2)
body.append(paragraph)

# title of second level:
title = Header(2, txt_b1)
body.append(title)

# Adding a basic Paragraph of plain text
paragraph = Paragraph(txt_b2)
body.append(paragraph)

if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_basic_text_document.odt")

# 3 - Saving Document
# Last but not least, don’t lose our hard work:
my_document.save(target=output, pretty=True)
# The pretty parameter asks for writing an indented serialized XML.
# The cost in space in negligible and greatly helps debugging,
# so don’t hesitate to use it.
