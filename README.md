# odfdo
Python library for OpenDocument format (ODF)


![logo](./odfdo.png)

`odfdo` is a Python3 library implementing the ISO/IEC 26300 OpenDocument Format
standard.

Project:
    https://github.com/jdum/odfdo

Author:
    jerome.dumonteil@gmail.com

License:
    Apache License, Version 2.0

`odfdo` is a derivative work of the former `lpod-python` project.


Installation
============

Installation from Pypi (recommended):

```python
pip install odfdo
```

Installation from sources (requiring setuptools):

```python
pip install .
```

After installation, you can check everything is working (requirement: `pytest`):

```python
pytest tests
```

The tests should run for a few seconds and issue no error.


Usage
=====


    from odfdo import Document, Paragraph

    doc = Document('text')
    doc.body.append(Paragraph("Hello world!"))
    doc.save("hello.odt")


tl;dr
=====

'Intended Audience :: Developers'


Documentation
=============

There is no detailed documentation or tutorial, but:

 - the `recipes` folder contains more than 50 working sample scripts,
 - the `doc` folder contains an auto generated documentation.

When installing odfdo, 4 scripts are installed:

 - `odfdo-diff`: show a *diff* between two .odt document.
 - `odfdo-folder`: convert standard ODF file to folder and files, and reverse.
 - `odfdo-show`: dump text from an ODF file to the standard output, and optionally styles and meta informations.
 - `odfdo-styles`: command line interface tool to manipulate styles of ODF files.

About styles: the best way to apply style is by merging styles from a template
document into your generated document (See `odfdo-styles` script).
Styles are a complex matter in ODF, so trying to generate styles programmatically
is not recommended.


Limitations
===========

`odfdo` is intended to facilitate the generation of ODF documents,
nevertheless a basic knowledge of the ODF format is necessary.

ODF document rendering can vary greatly from software to software. Especially the
"styles" of the document allow an adaptation of the rendering for a particular
software.

The best (only ?) way to apply style is by merging styles from a template
document into your generated document.

Related project
===============

I you work on .ods files (spreadsheet), you may be interested by these scripts that
use this library to parse/generate .ods files:
https://github.com/jdum/odsgenerator and https://github.com/jdum/odsparsator

Changes from former lpod library
================================
`lpod-python` was written in 2009-2010 as a Python 2.x library,
see: https://github.com/lpod/lpod-python

`odfdo` is an adaptation of this formaer project. `odfdo` main changes from `lpod`:

 - `odfdo` requires Python version 3.9 to 3.12. For Python 3.6 to 3.8 see previous releases.
 - API change: more pythonic.
 - include recipes.
 - use Apache 2.0 license.
