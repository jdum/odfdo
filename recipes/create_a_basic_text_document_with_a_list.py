#!/usr/bin/env python

import os

# Uncommented parts are explained in : create_a_basic_text_document.py

from odfdo import Document, List, ListItem

# Create the document
my_document = Document("text")
body = my_document.body

# Adding List
my_list = List(["Arthur", "Ford", "Trillian"])
# The list accepts a Python list of strings and list items.

# The list can be written even though we will modify it afterwards:
body.append(my_list)

# Adding more List Item to the list
item = ListItem("Marvin")
my_list.append_item(item)


if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_document_with_list.odt")

# And finally save the document.
my_document.save(target=output, pretty=True)

# it should contain only :
print(my_document.get_formatted_text())
# - Arthur
# - Ford
# - Trillian
# - Marvin
