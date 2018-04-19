#!/usr/bin/env python
"""
Remove the links (the text:a tag), keeping the inner text.
"""
import os
import sys

from odfdo import Document, Element


def get_default_doc():
    return "collection2.odt"


def remove_links(element):
    tag = 'text:a'
    keep_inside_tag = 'None'
    context = (tag, keep_inside_tag, False)
    element, is_modified = _tree_remove_tag(element, context)
    return is_modified


def _tree_remove_tag(element, context):
    """Remove tag in the element, recursive.
    - context = (tag to remove, protection tag, protection flag)
    - protection tag protect from change sub elements one sub level depth
    """
    buffer = element.clone
    modified = False
    sub_elements = []
    tag, keep_inside_tag, protected = context
    if keep_inside_tag and element.tag == keep_inside_tag:
        protect_below = True
    else:
        protect_below = False
    for child in buffer.children:
        striped, is_modified = _tree_remove_tag(
            child, (tag, keep_inside_tag, protect_below))
        if is_modified:
            modified = True
        if type(striped) == type([]):
            for item in striped:
                sub_elements.append(item)
        else:
            sub_elements.append(striped)
    if not protected and element.tag == tag:
        element = []
        modified = True
    else:
        if not modified:
            # no change in element sub tree, no change on element
            return (element, False)
        element.clear()
        try:
            for key, value in buffer.attributes.items():
                element.set_attribute(key, value)
        except ValueError:
            print("Bad attribute in", buffer)
    text = buffer.text
    tail = buffer.tail
    if text is not None:
        element.append(text)
    for child in sub_elements:
        element.append(child)
    if tail is not None:
        if type(element) == type([]):
            element.append(tail)
        else:
            element.tail = tail
    return (element, True)


if __name__ == "__main__":
    try:
        source = sys.argv[1]
    except IndexError:
        source = get_default_doc()

    document = Document(source)
    body = document.body

    print("Removing links from", source)
    print("'text:a' occurrences:", len(body.get_links()))

    remove_links(body)

    print("'text:a' occurrences after removal:", len(body.get_links()))

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = os.path.join('test_output', "my_" + source)

    document.save(target=output, pretty=True)
