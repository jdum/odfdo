# odfdo
python library for OpenDocument format (ODF)


![logo](./odfdo.png)

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


    sudo python setup.py install


after installation you can check everything is working:

    cd test && pytest
or

    cd test && python test.py


test should run for a few seconds and issue no error.


usage
=====


    from odfdo import Document, Paragraph

    doc = Document('text')
    doc.body.append(Paragraph("Hello world!"))
    doc.save("hello.odt")


tl;dr
=====

'Intended Audience :: Developers'


documentation
=============

 - the "recipes" folder contains more than 50 working sample scripts,
 - the "scripts" folder contains some useful scripts (like style management),
 - the "doc" folder contains auto generated documentation.

styles: the best way to apply style is by merging styles from a template
document into your generated document. See odfdo-style.py in "scripts" folder.


limitations
===========

odfdo is intended to facilitate the generation of ODF documents,
nevertheless a basic knowledge of the ODF format is necessary.

ODF document rendering can vary greatly from software to software. In
particular the "styles" of the document allow an adaptation of the rendering
for a particular software.

the best (only ?) way to apply style is by merging styles from a template
document into your generated document. See odfdo-style.py in "scripts" folder.


changes from former lpod library
================================
lpod-python was written in 2009-2010 as a python2 library,
see: https://github.com/lpod/lpod-python

odfdo main changes from lpod:

 - odfdo requires python version >= 3.6 (tested up to python 3.10)
 - API change: more pythonic
 - include recipes
 - use only Apache 2.0 license
