from odfdo import Document, List, ListItem

document = Document("text")
body = document.body
a_list = List(["chocolat", "café"])

item = ListItem("thé")
a_list.append(item)
