# odfdo

[![Release](https://img.shields.io/github/v/release/jdum/odfdo)](https://img.shields.io/github/v/release/jdum/odfdo)
[![Build Status](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch=devel)](https://img.shields.io/github/actions/workflow/status/jdum/odfdo/main.yml?branch%3Adevel)
[![License](https://img.shields.io/github/license/jdum/odfdo)](https://img.shields.io/github/license/jdum/odfdo)
[![PyPI Downloads](https://static.pepy.tech/badge/odfdo/month)](https://pepy.tech/projects/odfdo)

OpenDocument Format (ODF, ISO/IEC 26300) library for Python

![logo](https://raw.githubusercontent.com/jdum/odfdo/main/odfdo.png)

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
uv run pytest -n8
```

To generate the documentation in the `./docs` directory:

```bash
uv sync --group doc
uv run python doc_src/generate_doc.py
```

# Dependencies

The project is tested on Python 3.10 to 3.14 (Linux, Mac, Windows). See previous releases for earlier versions of Python.

A special effort has been made to limit the dependencies of this library: the only (non-development) dependency is `lxml`. The required versions of `lxml depend mainly on the version of Python used; see the `pyproject.toml` file for details. The project tries to keep up with `lxml` version updates regularly.

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
sheet = doc.body.get_sheet(0)

print(f"Value of A1: {sheet.get_cell('A1').value}")
sheet.set_value('B2', 'Updated Value')

doc.save('modified_spreadsheet.ods')
```

## Utilities

A few scripts are provided with `odfdo`:

-   `odfdo-diff`: show a _diff_ between the textual content of two ODT files.
-   `odfdo-folder`: a standard ODF file (zip archive) to a folder structure, or convert a folder structure back to an ODF file.
-   `odfdo-headers`: display the hierarchical headers (headings) of an ODF text document. The headers are printed with their numbering and can be limited by a specified depth.
-   `odfdo-highlight`: search for a regular expression pattern in an ODF text document and apply a highlighting style to the matching text. The style can include italic, bold, text color, and background color.
-   `odfdo-markdown`: convert an ODF text document to Markdown format and print to standard output.
-   `odfdo-replace`: find and replace text in an ODF file using a regular expression pattern.
-   `odfdo-show`: display various parts of an ODF document, including text content, styles, and metadata, to standard output or a specified directory.
-   `odfdo-styles`: manipulate styles within OpenDocument files: display, delete, or merge them.
-   `odfdo-table-shrink`: optimize the width and height of tables in an ODF spreadsheet by removing empty trailing rows and columns.
-   `odfdo-userfield`: inspect and modify user-defined fields within an ODF document.
-   `odfdo-from-csv`: import data from a CSV file into a new ODS (OpenDocument Spreadsheet) file. 
-   `odfdo-to-csv`: export a table from an ODS (OpenDocument Spreadsheet) file to a CSV file.
-   `odfdo-meta-print`: extract and display the metadata from an ODF file.
-   `odfdo-meta-update`: update the metadata of an ODF file by merging from a JSON file or stripping to minimal content.

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

If you work on `.ods` files (spreadsheet), you may be interested by these scripts using
this library to parse/generate `.ods` files:
[https://github.com/jdum/odsgenerator](https://github.com/jdum/odsgenerator) and [https://github.com/jdum/odsparsator](https://github.com/jdum/odsparsator)


# Former lpod-python library

`lpod-python` was written in 2009-2010 as a Python 2.x library,
see: `https://github.com/lpod/lpod-python`

`odfdo` is an adaptation of this former project to Python 3.x with several improvements.
