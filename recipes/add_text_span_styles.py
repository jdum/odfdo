#!/usr/bin/env python
"""
Transform a not styled document into a multi styled document, by changing
size and color of each parts of words.
"""
import sys, os
from random import randrange

from odfdo import Document, Style


def get_default_doc():
    return "dormeur_notstyled.odt"


def style_name():
    "returns a random style name"
    return 'rnd%s' % randrange(64)


if __name__ == "__main__":
    try:
        source = sys.argv[1]
    except IndexError:
        source = get_default_doc()

    document = Document(source)
    body = document.body

    print("Add some span styles to", source)
    # create some random text styles
    for i in range(64):
        style = Style(
            'text',
            name='rnd%s' % i,
            color=(randrange(256), randrange(256), randrange(256)),
            size="%s" % (8 + i / 5),
        )
        document.insert_style(style)

    words = set(body.text_recursive.split())
    for word in words:
        name = style_name()
        style = document.get_style('text', name)
        for paragraph in body.get_paragraphs() + body.get_headers():
            # apply style to each text matching with the regex of some word
            paragraph.set_span(name, regex=word)

    if not os.path.exists('test_output'):
        os.mkdir('test_output')

    output = "my_span_styled_" + source
    #document.save(target=os.path.join('test_output', output), pretty=True, packaging='folder')
    document.save(target=os.path.join('test_output', output), pretty=True)
