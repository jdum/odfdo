from odfdo import Document, List, ListItem

document = Document("text")
body = document.body

my_list = List(["chocolat", "café"])
body.append(my_list)

item = ListItem("thé")
my_list.append(item)

# A sublist is simply a list as an item of another list

item.append(List(["thé vert", "thé rouge"]))

print(body.serialize(True))
