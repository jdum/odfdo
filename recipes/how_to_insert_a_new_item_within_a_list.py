from odfdo import Document, List

document = Document('text')
body = document.body

my_list = List(['chocolat', 'café'])

# In case your forgot to insert an important item:
my_list.insert_item("Chicorée", position=1)

# Or you can insert it before another item:
cafe = my_list.get_item(content="café")
my_list.insert_item('Chicorée', before=cafe)

# Or after:
my_list.insert_item("Chicorée", after=cafe)
