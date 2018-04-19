# odfdo
python library for OpenDocument format (ODF)

odfdo
=====

odfdo is a Python3 library implementing the ISO/IEC 26300 OpenDocument Format
standard.

project:
    https://github.com/jdum/odfdo

author:
    jerome.dumonteil@gmail.com

licence:
    Apache License, Version 2.0

odfdo is a derivative work of the lpod-python project.

installation
============

    `sudo python setup.py install`


after installation you can check everything is working:
    `cd test`
    `python test.py`

test should run for a few seconds and issue not errors.


usage
=====

`from odfdo import Document, Paragraph`
``
`doc = Document('text')`
`doc.body.append(Paragraph("Hello world!"))`
`doc.save("hello.odt")`

documentation
=============

 - the "recipes" folder contains more than 50 working sample scripts,
 - the "scripts" folder contains usefull scripts (like style management),
 - the "doc" folder contains auto generated documentation.

styles: the best way to apply style is by merging styles from a template
document into your generated document. See odfdo-style.py in "scripts" folder.


changes from lpod
=================

odfdo main changes from lpod:
- odfdo requires python version >= 3.5
- API change: more pythonic
- include recipes
- use only Apache 2.0 license


about former lpod-python
========================
lpod-python was written in 2009-2010 as a python2 libry implementing:
libarylpOD Project (Languages & Platforms OpenDocument, definition of a
Free Software API implementing the ISO/IEC 26300 standard).

The most recent version of lpod-python is there:

    https://github.com/lpod/lpod-python

Architect: Jean-Marie Gouarné <jean-marie.gouarne@arsaperta.com>
Coordinator: Luis Belmar-Letelier <luis@itaapy.com>
