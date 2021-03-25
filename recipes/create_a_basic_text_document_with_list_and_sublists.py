#!/usr/bin/env python
import os

# Uncommented parts are explained in : create_a_basic_document_with_a_list.py

from odfdo import Document, List, ListItem

# Create the document
my_document = Document("text")
body = my_document.body

# Adding List
my_list = List(["Arthur", "Ford", "Trillian"])
item = ListItem("Marvin")
my_list.append_item(item)
body.append(my_list)

# Adding Sublist¶
# A sublist is simply a list as an item of another list:
item.append(List(["Paranoid Android", "older than the universe"]))

# See the result:
print(my_document.get_formatted_text())
# - Arthur
# - Ford
# - Trillian
# - Marvin
#   - Paranoid Android
#   - older than the universe


# Inserting List Item
# In case your forgot to insert an item:
my_list.insert_item("some dolphins", position=1)

# Or you can insert it before another item:
marvin = my_list.get_item(content="Marvin")
my_list.insert_item("Zaphod", before=marvin)
# Or after:
my_list.insert_item("and many others", after=marvin)


if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_document_with_sublist.odt")

# And finally save the document.
my_document.save(target=output, pretty=True)

# See the result:
print(my_document.get_formatted_text())
# - Arthur
# - some dolphins
# - Ford
# - Trillian
# - Zaphod
# - Marvin
#   - Paranoid Android
#   - older than the universe
# - and many others
