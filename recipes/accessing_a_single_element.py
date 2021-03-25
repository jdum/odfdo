#!/usr/bin/env python

from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
filename = "collection2.odt"

doc = Document(filename)

# The body object is an XML element from which we can access one or several
# other elements we are looking for.
body = doc.body

# Accessing a single element
# To access a single element by name, position or a regular expression on
# the content, use get_xxx_by_<criteria>, where criteria can be position,
# content, or for some of them name, id title, description.
print("- Content of the first footnote:")
print(body.get_note(position=0).text_recursive)
print("- Content of the paragraph with the word 'Fish'")
print(body.get_paragraph(content="Fish").text_recursive)
print("- Content of the first Title:")
print(body.get_header(position=0).text_recursive)
print("- Content of the last Title:")
print(body.get_header(position=-1).text_recursive)

Expected_result = """
- Content of the first footnote:
1Gaiman, Neil (2003). Don't Panic: Douglas Adams and the "Hitchhiker's Guide to
the Galaxy". Titan Books. pp. 144–145. ISBN 1-84023-742-2.
- Content of the paragraph with the word 'Fish'
  In So Long, and Thanks for All
  the Fish (published in 1984), Arthur returns home to Earth, rather
  surprisingly since it was destroyed when he left. He meets and falls in love
  with a girl named Fenchurch, and discovers this Earth is a replacement
  provided by the dolphins in their Save the Humans campaign. Eventually he
  rejoins Ford, who claims to have saved the Universe in the meantime, to
  hitch-hike one last time and see God's Final Message to His Creation. Along
  the way, they are joined by Marvin, the Paranoid Android, who, although 37
  times older than the universe itself (what with time travel and all), has just
  enough power left in his failing body to read the message and feel better
  about it all before expiring.
- Content od the first Title:
The Hitchhiker's Guide to the Galaxy
- Content od the last Title:
Official sites
"""
