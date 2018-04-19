#!/usr/bin/env python

import os

from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
filename = "collection2.odt"

style_filename = "lpod_styles.odt"  # copied here from the odfdo package

# We want to change the styles of the collection2.odt.
# We know the odfdo_styles.odt document contains an interesting style.
# So let’s first fetch the style:
style_document = Document(style_filename)

# Open our document:
document = Document(filename)

# We could change only some styles, but here we want a clean basis:
document.delete_styles()

# And now the actual style change:
document.merge_styles_from(style_document)


if not os.path.exists('test_output'):
    os.mkdir('test_output')

# Saving the document (with a different name)
document.save(target=os.path.join('test_output', "my_collection_styled.odt"),
              pretty=True)

################################################################################
# For more advanced version, see the odfdo-style.py script in scripts folder   #
################################################################################
