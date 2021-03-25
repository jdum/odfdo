from odfdo import Document, List, ListItem

document = Document("text")
body = document.body
my_list = List(["chocolat", "café"])

item = ListItem("thé")
my_list.append(item)
