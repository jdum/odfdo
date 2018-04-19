#  Adding a table of content to an existing text document.
from odfdo import Document, Paragraph, TOC

document = Document('text')
body = document.body

# The TOC element comes from the toc module
#

toc = TOC()
body.append(toc)
