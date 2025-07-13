# odfdo

[![Release](https://img.shields.io/github/v/release/jdum/odfdo)](https://img.shields.io/github/v/release/jdum/odfdo)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch=devel)](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch%3Adevel)
[![License](https://img.shields.io/github/license/jdum/odfdo)](https://img.shields.io/github/license/jdum/odfdo)
[![PyPI Downloads](https://static.pepy.tech/badge/odfdo/month)](https://pepy.tech/projects/odfdo)

OpenDocument Format (ODF, ISO/IEC 26300) library for Python

![logo](https://raw.githubusercontent.com/jdum/odfdo/master/odfdo.png)

`odfdo` is a Python library for programmatically creating, parsing, and editing OpenDocument Format (ODF) files.  It provides an interface for interacting with `.odt`, `.ods`, `.odp`, and other ODF file types. The library comes with a set of utilities and recipes for common actions to make it easier to use.

-   Document Creation: Generate new ODF documents.
-   Content Manipulation: Add, modify, or delete text, paragraphs or tables.
-   Table Operations: Create, populate, and modify tables.
-   Style Management: Control formatting through different ways.
-   Drawing and Presentation: Less advanced features, but allow work with elements in `.odg` and `.odp` files.
-   Metadata: Read and write document metadata.

Project:
[https://github.com/jdum/odfdo](https://github.com/jdum/odfdo)

Author:
jerome.dumonteil@gmail.com

License:
Apache License, Version 2.0

`odfdo` is a derivative work of the former `lpod-python` project.

# Installation

Installation from Pypi (recommended):

```bash
pip install odfdo
```

Installation from sources:

```bash
uv sync
```

After installation from sources, you can check everything is working. The tests should run for a few seconds and issue no error.

```bash
uv sync --dev
uv run pytest
```

To generate the documentation in the `./docs` directory:

```bash
uv sync --group doc
uv run python doc_src/generate_doc.py
```

A special effort has been made to limit the dependencies of this library: the only (non-development) dependency is `lxml`. Versions of `lxml` depend mainly on the version of Python used; see the `pyproject.toml` file for details.


# Usage Overview

## Creating a "Hello world" Text Document

```python
from odfdo import Document, Paragraph

doc = Document('text')
doc.body.append(Paragraph("Hello world!"))

doc.save("hello.odt")
```

## Modifying a Spreadsheet

```python
from odfdo import Document

doc = Document('existing_spreadsheet.ods')
sheet = doc.body.get_table(0)

print(f"Value of A1: {sheet.get_cell('A1').value}")
sheet.set_value('B2', 'Updated Value')

doc.save('modified_spreadsheet.ods')
```

## Utilities

A few scripts are provided with `odfdo`:

-   `odfdo-diff`: show a _diff_ between two .odt document.
-   `odfdo-folder`: convert standard ODF file to folder and files, and reverse.
-   `odfdo-headers`: print the headers of an ODF file.
-   `odfdo-highlight`: highlight the text matching a pattern (regex) in an ODF file.
-   `odfdo-markdown`: export text document in Markdown format to stdout.
-   `odfdo-replace`: find a pattern (regex) in an ODF file and replace by some string.
-   `odfdo-show`: dump text from an ODF file to the standard output, and optionally styles and meta informations.
-   `odfdo-styles`: command line interface tool to manipulate styles of ODF files.
-   `odfdo-table-shrink`: shrink tables to optimize width and height.
-   `odfdo-userfield`: show or set the user-field content in an ODF file.


# tl;dr

'Intended Audience :: Developers'

# Documentation

-   the `recipes` folder contains more than 60 working sample scripts,
-   the auto-generated documentation exposes public APIs and recipes.

Online documentation: [https://jdum.github.io/odfdo](https://jdum.github.io/odfdo/)

# About styles

The best way to apply style is by merging styles from a template
document into your generated document (See `odfdo-styles` script).
Styles are a complex matter in ODF, so trying to generate styles programmatically is not recommended.
Several recipes provide an example of manipulating styles, including: `change_paragraph_styles_methods.py`,`create_basic_text_styles`, `add_text_span_styles`.


# Related project

I you work on `.ods` files (spreadsheet), you may be interested by these scripts using
this library to parse/generate `.ods` files:
[https://github.com/jdum/odsgenerator](https://github.com/jdum/odsgenerator) and [https://github.com/jdum/odsparsator](https://github.com/jdum/odsparsator)


# Former lpod-python library

`lpod-python` was written in 2009-2010 as a Python 2.x library,
see: `https://github.com/lpod/lpod-python`

`odfdo` is an adaptation of this former project to Python 3.x with several improvements.
