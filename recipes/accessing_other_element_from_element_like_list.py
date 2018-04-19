#!/usr/bin/env python

from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
filename = "collection2.odt"

doc = Document(filename)

# The body object is an XML element from which we can access one or several
# other elements we are looking for.
body = doc.body

# Any element is a context for navigating but only on the subtree it
# contains. Just like the body was, but since the body contains all content,
# we didn’t see the difference.
# Let's try the lists:
print("Available lists of the document:", len(body.get_lists()))

mylist = body.get_list(position=4)
print(mylist)
print("The 4th list got paragraphs:", len(mylist.get_paragraphs()))

# Now print the list content
for paragraph in mylist.get_paragraphs():
    print(paragraph)
    print(paragraph.text_recursive)

Expected_result = """
Available lists of the document: 5
<lpod.list.odf_list object at 0x1018434d0> "text:list"
The 4th list got paragraphs: 9
<lpod.paragraph.odf_paragraph object at 0x101843650> "text:p"
BBC Cult website, official website for the TV show version (includes information, links and downloads)
<lpod.paragraph.odf_paragraph object at 0x101843690> "text:p"
BBC Radio 4 website for the 2004-2005 series
<lpod.paragraph.odf_paragraph object at 0x101843610> "text:p"
Official Movie Site
<lpod.paragraph.odf_paragraph object at 0x101843550> "text:p"
The Hitchhiker's Guide to the Galaxy (2005 movie) at the Internet Movie Database
<lpod.paragraph.odf_paragraph object at 0x1018436d0> "text:p"
The Hitch Hikers Guide to the Galaxy (1981 TV series) at the Internet Movie Database
<lpod.paragraph.odf_paragraph object at 0x101843710> "text:p"
h2g2
<lpod.paragraph.odf_paragraph object at 0x101843750> "text:p"
Encyclopedia of Television
<lpod.paragraph.odf_paragraph object at 0x101843790> "text:p"
British Film Institute Screen Online page devoted to the TV series
<lpod.paragraph.odf_paragraph object at 0x101843510> "text:p"
DC Comics H2G2 site
"""
