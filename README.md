# odfdo

[![Release](https://img.shields.io/github/v/release/jdum/odfdo)](https://img.shields.io/github/v/release/jdum/odfdo)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch=devel)](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch%3Adevel)
[![License](https://img.shields.io/github/license/jdum/odfdo)](https://img.shields.io/github/license/jdum/odfdo)
[![PyPI Downloads](https://static.pepy.tech/badge/odfdo/month)](https://pepy.tech/projects/odfdo)

Python library for OpenDocument format (ODF)

![logo](https://raw.githubusercontent.com/jdum/odfdo/master/odfdo.png)

`odfdo` is a Python3 library implementing the ISO/IEC 26300 OpenDocument Format
standard.

Project:
https://github.com/jdum/odfdo

Author:
jerome.dumonteil@gmail.com

License:
Apache License, Version 2.0

`odfdo` is a derivative work of the former `lpod-python` project.

# Installation

Installation from Pypi (recommended):

```python
pip install odfdo
```

Installation from sources (requiring setuptools):

```python
pip install .
```

After installation from sources, you can check everything is working (some requirements: `pytest`, Pillow, ...):

```python
pytest
```

The tests should run for a few seconds or minutes and issue no error.

The full test suite uses `tox` to check different `Python` and `lxml` versions.

A special effort is made to limit the dependencies of this library: the only dependency (outside development) is `lxml`. The `lxml` versions depend mainly on the version of Python used, see the `pyproject.toml` file for details.

# Usage

    from odfdo import Document, Paragraph

    doc = Document('text')
    doc.body.append(Paragraph("Hello world!"))
    doc.save("hello.odt")

# tl;dr

'Intended Audience :: Developers'

# Documentation

There is no detailed documentation or tutorial, but:

-   the `recipes` folder contains more than 60 working sample scripts,
-   the `doc` folder contains an auto generated HTML documentation, including recipes.

When installing odfdo, a few scripts are installed:

-   `odfdo-diff`: show a _diff_ between two .odt document.
-   `odfdo-folder`: convert standard ODF file to folder and files, and reverse.
-   `odfdo-show`: dump text from an ODF file to the standard output, and optionally styles and meta informations.
-   `odfdo-styles`: command line interface tool to manipulate styles of ODF files.
-   `odfdo-replace`: find a pattern (regex) in an ODF file and replace by some string.
-   `odfdo-userfield`: show or set the user-field content in an ODF file.
-   `odfdo-highlight`: highlight the text matching a pattern (regex) in an ODF file.
-   `odfdo-headers`: print the headers of an ODF file.
-   `odfdo-table-shrink`: shrink tables to optimize width and height.
-   `odfdo-markdown`: export text document in Markdown format to stdout.

About styles: the best way to apply style is by merging styles from a template
document into your generated document (See `odfdo-styles` script).
Styles are a complex matter in ODF, so trying to generate styles programmatically
is not recommended.

# Limitations

`odfdo` is intended to facilitate the generation of ODF documents,
nevertheless a basic knowledge of the ODF format is necessary.

ODF document rendering can vary greatly from software to software. Especially the
"styles" of the document allow an adaptation of the rendering for a particular
software.

The best (only ?) way to apply style is by merging styles from a template
document into your generated document. However a few recipes show how to make
programmatically some basic styles: `create_basic_text_styles`, `add_text_span_styles`).

# Related project

I you work on `.ods` files (spreadsheet), you may be interested by these scripts using
this library to parse/generate `.ods` files:
`https://github.com/jdum/odsgenerator` and `https://github.com/jdum/odsparsator`

# Changes from former lpod library

`lpod-python` was written in 2009-2010 as a Python 2.x library,
see: `https://github.com/lpod/lpod-python`

`odfdo` is an adaptation of this former project. `odfdo` main changes from `lpod`:

-   `odfdo` requires Python version 3.9 to 3.13. For previous Python versions see older releases.
-   API change: more pythonic.
-   include recipes.
-   use Apache 2.0 license.
