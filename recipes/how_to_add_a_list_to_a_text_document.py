from odfdo import Document

document = Document('text')
body = document.body

# Lists are a dedicated object
from odfdo import List
my_list = List(['chocolat', 'café'])

# The list factory accepts a Python list of strings and list items.
#
# The list can be written even though we will modify it afterwards:

body.append(my_list)
