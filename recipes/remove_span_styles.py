#!/usr/bin/env python
"""
Remove span styles (like some words in bold in a paragraph), except in titles.
"""
import os
import sys

from odfdo import Document, Element


def get_default_doc():

    return "dormeur.odt"


def remove_text_span(element):
    tag = 'text:span'
    keep_inside_tag = 'text:h'
    context = (tag, keep_inside_tag, False)
    element, is_modified = _tree_remove_tag(element, context)
    return is_modified


def _tree_remove_tag(element, context):
    """Send back a copy of the element, without span styles. Element should be
    either paragraph or heading
    - context = (tag to remove, protection tag, protection flag)
    - protection tag protect from change any sub elements one level depth
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

    print("Removing span styles from", source)
    print("'text:span' occurrences:", len(body.get_spans()))

    remove_text_span(body)

    print("'text:span' occurrences after removal:", len(body.get_spans()))

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = os.path.join('test_output', "my_RS_" + source)

    document.save(target=output, pretty=True)
