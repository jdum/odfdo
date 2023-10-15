from odfdo import Document, List

document = Document("text")
body = document.body

a_list = List(["chocolat", "café"])

# In case your forgot to insert an important item:
a_list.insert_item("Chicorée", position=1)

# Or you can insert it before another item:
cafe = a_list.get_item(content="café")
a_list.insert_item("Chicorée", before=cafe)

# Or after:
a_list.insert_item("Chicorée", after=cafe)
