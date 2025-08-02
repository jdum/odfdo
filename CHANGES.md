# Odfdo Release Notes

## [3.16.0] - 2025-08-02

-  Added methods to set the default document language, both in the default styles (the value used by LibreOffice) and in the metadata. In short: using the new property `Document.language = "en-US"` will make `Document.langusge` value to "en-US", both the default styles and meta fields now have this value.
- Small fixes in the Style properties management.

### Changed

-   Move `is_RFC3066()` test from `Meta._is_RFC3066()` to `utils.is_RFC3066()`.

### Added

-   Add warnings in `meta.py` docstring methods about default language.
-   Add methods `styles.set_default_styles_language_country()`, `styles.get_default_styles()`, `Document.get_language()`, `Document.set_language()`.
-   Add properties `styles.default_styles`, `styles.default_language`, `Document.language`.
-   Add tests for `Document.language`.

### Fixed

-   Fix `style:use-window-font-color` beeing a color, which is not.
-   Fix `style.set_properties()` broken for unknown properties.

## [3.15.1] - 2025-07-26

-  Refactor of code (type hints).

### Changed

-  Refactor `odfdo` modules for type hints: `reference`. `container`. `named_range`. `mixin_paragraph`. `mixin_paragraph_formatted`, `element`. `mixin_dc_creator`, `line_break`, `element_typed`, `container`, `body`, `xmlpart`.

## [3.15.0] - 2025-07-20

-  For concept clarity, rename iterator methods `Table.traverse()` to `Table.iter_rows()`, `Table.traverse_columns()` to `Table.iter_columns()`, `Row.traverse()` to `Row.iter_cells()`, maintaining compatibility with aliases on previous names.
-  Add alias names for `Body.get_table()`, `tables`, `get_table()`: `get_sheets()`, `sheets`, `get_sheet()`.
-  Add the `Meta.strip()` method to clean all metadata from a document and a recipe showing how it works.
-  Improve the `remove_tree()` utility function (used in recipes) by adding the `keep_children` argument.
-  Optimize access to columns in tables.
-  Refactor of code (type hints) and improvement of the tests coverage.

### Changed

-   Rename `Table.traverse()` -> `Table.iter_rows()`, keep compatibility (alias nane).
-   Rename `Table.traverse_columns()` -> `Table.iter_columns()`, keep compatibility (alias nane).
-   Rename `Row.traverse()` -> `Row.iter_cells()`, keep compatibility (alias nane).
-   Refactor methods `set_span()` and `set_link()`.
-   Refactor `Tab.text` property.
-   Refactor modules `odfdo.table_cache`. `odfdo.container`. `odfdo.named_range`.
-   Refactor generic getter/setter in module `odfdo.element`.
-   Use the cache to iterate over columns in tables.

### Added

-   Add aliases for `Body.get_table`, `tables`, `get_table`: `get_sheets`, `sheets`, `get_sheet`.
-   Add argument "keep_children" to `remove_tree()` utility function, add tests for `remove_tree()`.
-   Add method `how_to_remove_all_meta_data.py`.
-   Add recipe `Meta.strip()`.
-   Add tests for module `odfdo.TOC`.
-   Add test for `Column`.
-   Add tests for module `odfdo.table_cache`.
-   Add tests for module `odfdo.named_range`.
-   Add tests for module `odfdo.spacer`.

### Fixed

-   Fix crashing test in test suite for markdown.

## [3.14.10] - 2025-07-14

-   Improve documentation and docstrings.
-   Move classes `Column`, `Annotation`,user fields, `Spacer`, `Tab`,`Spacer`,`LineBreak`, and `Span` to their own module (compatibilty maintained with previous versions).
-   Minor fixes on classes `odfdo.variable.VarSet` and `odfdo.variable.VarTime`.
-   Refactor of code and improvement of the tests coverage.

### Changed

-   Improve test coverage for module `odfdo.meta`.
-   Improve test coverage for module `odfdo.xpath_query`.
-   Improve test coverage for module `odfdo.utils`.
-   Improve test coverage for module `odfdo.mixin_paragraph`.
-   Improve test coverage for module `odfdo.header`.
-   Improve test coverage for module `odfdo.variable`.
-   Improve test coverage for module `odfdo.user_field`.
-   Improve test coverage for module `odfdo.image`.
-   Improve test coverage for module `odfdo.list`.
-   Improve test coverage for module `odfdo.draw_page`.
-   Improve test coverage for module `odfdo.xmlpart`.
-   Improve test coverage for module `odfdo.datatype`.
-   Improve test coverage for module `odfdo.styles`.
-   Improve test coverage for markdown mixin.
-   Replace `ParagraphBase` by a mixin.
-   Move class `Annotation` from `odfdo.note` module to module `odfdo.annotation`.
-   Move classes about user fields from `odfdo.variable` module to module `odfdo.user_field`.
-   Move class `Spacer` from `odfdo.paragraph_base` module to module `odfdo.spacer`.
-   Move class `Tab` from `odfdo.paragraph` module to module `odfdo.tab`.
-   Move class `LineBreak` from `odfdo.paragraph` module to module `odfdo.line_break`.
-   Move class `Span` from `odfdo.paragraph` module to module `odfdo.span`.
-   Refactor module `odfdo.variable`.
-   Refactor module `odfdo.xmlpart`.
-   Refactor module `odfdo.datatype`.
-   Refactor module `odfdo.mixin_paragraph`.
-   Update some docstrings.
-   Update Readme.

### Added

-   Add tests for typed elements classes (variables).
-   Add more `Unit` conversions to pixel, add test for `Unit` class.
-   Add argument `node_type` to `DrawPage.set_transition()`.

### Fixed

-   Fix `odfdo.variable.VarSet`: keep style when set a value.
-   Fix `odfdo.variable.VarTime` attribute time_adjust.

## [3.14.9] - 2025-07-08

-   Improve documentation and docstrings.
-   Move classes `Column` and `NamedRange` to their own module (compatibilty maintained with previous versions).
-   Refactor of code and improvement of the tests coverage.

### Changed

-   Move class `Column` from `odfdo.table` module to module `odfdo.column`.
-   Move class `NamedRange` from `odfdo.table` module to module `odfdo.named_range`.
-   Refactor classes `NamedRange`.
-   Refactor module `odfdo.tracked_changes`.
-   Refactor module `odfdo.note`.
-   Improve test coverage of tracked changes related classes.
-   Improve test coverage for module `odfdo.note`.
-   Documentation: show table of contents for recipes, add logo.
-   Update many docstrings.
-   Update Readme.

### Added

-   Add tests for modules `odfdo.smil`, `odfdo.reference`.

### Removed

-   Remove deprecated `gen_doc.sh`.

### Fixed

-   Fix style argument of function `import_from_csv()`.
-   Fix `dc_creator` and `dc_date` for tracked changes use.

## [3.14.8] - 2025-07-06

-  Publish documentation on https://jdum.github.io/odfdo/
-  The previous ./doc directory is removed, documentation can be generated locally, see README.md

### Changed

-   documentation now generated by script `generate_doc.py` in directory `doc_src`.

## [3.14.7] - 2025-07-06

-   Fixes for rare situations on table of contents without title, creation of `Annotation`, empty `Tables` optimization.
-   Cosmetic improvement of Markdown export of small tables.
-   Added the `util.remove_tree()` function, used in a few recipes, to recursively remove a tag
-   Technical updates: refactor all recipes to have the same structure, small refactoring of code and tests.

### Changed

-   Refactor all recipes.
-   Small refactoring of `Element`class for better type hints.
-   Improve markdown export of small tables.
-   Configure test coeverage.

### Added

-   Added the `util.remove_tree()` function.
-   Add tests for `odfdo.toc` module

### Fixed

-   Allow `Table.optimize_width()` to optimize an empty table.
-   Fix `Annotation` creation with a name passed as argument.
-   Fix `TOC` having empty title.

## [3.14.6] - 2025-06-29

-   Add support for the `lxml` library version 6.0.0.
-   Fix a slowness of `odfdo-show`on big tables.
-   Technical updates: refactor internal cache for `Table` and `Row`, add tests for `Row` class, improve typing and doc strings on module `odfdo.element`, improve test suite speed.

### Changed

-   Refactor cache system in `Row` and `Table` methods.
-   Refactor `Element`class for better type hints.
-   Configure test suite using `pytest-xdist`

### Added

-   Add internal module `odfdo.table_cache` with classes `RowCache`, `TableCache`.

### Fixed

-   Fix `odfdo-show` slowness on big tables.

## [3.14.5] - 2025-06-28

-   Improve CVS conversion: refactor `Table.to_csv()`, `import_from_csv()`, add classmethod `Table.from_csv()`, and add recipes `export_tables_to_csv_format` and `import_csv_content_into_a_table`.
-   Add recipe `how_to_add_a_right_aligned_picture_to_a_text_document`.
-   Technical updates: refactoring of Table iterators and some recipes' code, configure `mypy` code analysis and refactoring.

### Changed

-   Refactor `Table.to_csv()`, `import_from_csv()`.
-   Refactor recipes: `change_paragraph_styles_methods`, `change_values_of_a_chart_inside_a_document`, `concatenate_presentations`, `copy_style_from_another_document`.
-   Refactor `Table.traverse_columns()` iterator.
-   Refactor `Row.traverse()`.
-   Remove unused cache for columns.
-   start work on mypy configuration and analysis.

### Added

-   Add classmethod `Table.from_csv()`.
-   Add recipes `export_tables_to_csv_format.py` and `import_csv_content_into_a_table.py`.
-   Add recipe `how_to_add_a_right_aligned_picture_to_a_text_document`.

## [3.14.4] - 2025-06-21

-   Technical updates: refactoring of some recipes' code and improvement of test coverage.
-   Improve `README.md`

### Changed

-   Refactor recipes: `remove_span_styles`, `make_a_presentation_from_text_with_different_styles`, `how_to_add_a_table_to_a_document`, `get_text_content_from_odt_file`, `change_image_in_many_documents`, `basic_presentation_hello_world`, `add_text_span_styles`, `add_private_annotations_to_a_document`, `add_logo_on_presentation`, `add_a_custom_footer_to_a_text_document`, `accessing_other_element_from_element_like_list`, `accessing_a_single_element.py accessing_a_list_of_elements`, `accessibility_check_on_a_document`.
-   Improve tests for table coordinates, `MetaAutoReload`, `Link`, `Manifest`, `Meta`, `Content`, `MetaHyperlinkBehaviour`, `Row`.

## [3.14.3] - 2025-06-14

-   The rarely used `RowGroup` class is moved to a dedicated module and tests are added for this class. A new property `Table.row_groups` returning the list of row groups of the table is available.
-   A new recipe explains how to add a page footer by using the method `Style.set_page_footer()`.
-   Compatibility with previous versions is maintained.

### Changed

-   The `RowGroup` class is moved to a dedicated module.
-   Refactoring of the `RowGroup` class.
-   Small refactoring of `Cell.repeated` setter.
-   Refactor recipe `create_a_text_document_with_tables_in_it.py`.
-   Update versions of development dependencies.

### Added

-   Add a new property `Table.row_groups`.
-   Add tests for the `RowGroup` class.
-   Add recipe `add_a_custom_footer_to_a_text_document.py`.

### Fixed

-   Fix some `Xpath` commands to fetch rows inside row groups.
-   Fix `Style.set_page_footer()` when the new footer is a string.

## [3.14.2] - 2025-06-07

-   The `Style` class for the `table` area accepts two new arguments useful for a table in a text context: 'width' and 'align'. Example: `Style("table", "style_name", width="5cm", align="left", margin_left="2cm")`.
-   `Cell.date` property now returns `datetime.date` type (was `datetime.datetime`). `Cell.value` still returns a `datetime.datetime`. Note: OpenDocument format does not differentiate between "date" and "datetime", so `Cell.date` and `Cell.datetime` are best guesses in case the user expects such a specific value.
-   Allow to use string to define width and height in Table creation, ie `table = Table("table", width="4")`
-   Compatibility with previous versions is maintained, at the exception of `Cell.date` type.

### Changed

-   `Cell.date` property now returns `datetime.date`.
-   Allow use of string when defining Table height and width.

### Added

-   Style class for area 'table' accepts two new argumaents: 'width' and 'align'.
-   Add more tests for Cell class coverage.

### Fixed

-   Allow decode boolean from bytes (mostly for test coverage).
-   An Exception type was missing in `Cell.decimal`.
-   Fix docstrings of modules.

## [3.14.1] - 2025-06-01

-   Technical updates: code refactoring. Compatibility with previous versions is maintained.

### Changed

-   Refactor `Paragraph._by_regex_offset` method.
-   Move `CSS3_COLORMAP` constant in utils directory. Link with previous location in `odfdo.const` is kept for compatibility.
-   Refactor `Element.text_content` property.

### Added

-   Add `utils/css3_colormap.py` file.

## [3.14.0] - 2025-05-26

-   Improve methods for retrieving information from cells spanned in tables.

    -   Add boolean argument `covered` to the method `Cell.is_spanned()`. If `covered` is set to True (the default), all covered cells of the spanned area return True, otherwise, only the top-left cell returns True. The top-left cell in the spanned area contains the `"table:number-columns-spanned"` and `"table:number-rows-spanned "` attributes. The default behavior of `Cell.is_spanned()` remains unchanged from previous versions.

    -   Add `Cell.is_covered()` method: returns whether the cell is covered (`table:covered-table-cell` tag), meaning it is part of a spanned area of cells, but not the top-left one.

    -   Add `Cell.span_area()` method:  returns the tuple (number of columns, number of rows) of the area covered by a spanned cell. If the cell is not spanned, returns (0, 0).

-   Small refactoring in `coordinates.py`.

### Changed

-   Add boolean argument `covered` to the method `Cell.is_spanned()`. The default behavior of `Cell.is_spanned()` remains unchanged from previous versions.
-   Small refactoring in `coordinates.py`.
-   Update test suite.

### Added

-   Add `Cell.is_covered()` method.
-   Add `Cell.span_area()` method.

## [3.13.12] - 2025-05-17

Technical updates: refactor code for isiterable() function, define Unit class in its own file, apply ruff.

### Changed

-   Define Unit class in its own file odfdo.unit.py (previous import from odfdo.datatype is still allowed to maintain compatibility).
-   Refactor code of isiterable() function.

## [3.13.11] - 2025-05-10

Added `lxml` version 5.4.0 to the test suite.
Technical updates: refactor code for get_formatted_text() and Element.get_value().

### Changed

-   Refactor code for get_formatted_text().
-   Refactor code for Element.get_value().

### Added

-   Version 5.4.0 of `lxml` added to `tox.ini`.

## [3.13.10] - 2025-04-20

Add a method to set the metadata of the document from a Python dict.
Added `lxml` version 5.3.2 to the test suite.
Fix incorrect docstring of DrawImage (issue 56).
Technical update: apply more ruff's style recommendations.

### Changed

-   Apply ruff's style recommendations.

### Added

-   Add methods: `Meta.from_dict()`.
-   Version 5.3.2 of `lxml` added to `tox.ini`.

### Fixed

-   Update incorrect docstring of DrawImage.

## [3.13.9] - 2025-03-22

Technical update: migrate from `poetry` build environment to `uv`, and reorganize tests.

### Changed

-   Migrate from `poetry` build environment to `uv`
-   Organize tests with more fixtures and sub directories.

## [3.13.8] - 2025-03-15

Technical update: update `poetry` to version 2.1, reformat `pyproject.toml`, move source code in the `src` directory.

### Changed

-   The source code is now in the `src` sub directory.
-   Build of the library requires `poetry` version 2.0 or more.

## [3.13.7] - 2025-03-08

Improved filter on allowed characters in a table name (for compatibility with allowed names in LibreOffice). Forbidden characters are now `\n` `\` `/` `*` `?` `:` `[` `]`, and `"'"` as first or last character. Previously forbidden characters were simply `\n` `/` `\` `"'"`.

Added `lxml` version 5.3.1 to the test suite.

### Changed

-   The regex for unauthised characters in table names is now: `r"^\'|[\n\\/\*\?:\][]|\'$"`.

### Added

-   Version 5.3.1 of `lxml` added to `tox.ini`.


## [3.13.6] - 2025-02-04

Fix corrupted ODF file due to incoherent manifest files, especially in .odg files (issue 54).

### Fixed

-   Fixed `Document.save()` check for `manifest.rdf` listed in `manifest.xml`

## [3.13.5] - 2025-01-25

Add the option `formatted` to script `odfdo-replace` and method `Element.replace()` to interpret the `<space>`, `<tab>` and `<CR>` of the replacement string.

### Added

-   Add `Element.replace()` optional argument `formatted`
-   Add `odfdo-replace` optional option `--formatted`

## [3.13.4] - 2025-01-22

-   Fix a bug on `Document.insert_style()` and related methods that prevented
the loading of styles from the family `number:*`, like `number:currency-style` (issue #53).

### Fixed

-   Fixed `Document.insert_style()` and `CONTEXT_MAPPING` in `styles.py` for a better detection of styles pseudo-families.

## [3.13.3] - 2025-01-01

-   Refactor cell properties to get easier and more consistent access to cell values. Some new properties added: Cell.decimal, Cell.int, Cell.bool, Cell.duration, Cell.datetime, Cell.date.
-   Add a `.rdf` manifest file if it is missing (this should only happen in very rare manipulations).

### Changed

-   Refactoring of Cell properties.
-   Refactoring of Container class to ensure creation of manifest file.

### Added

-   Add properties: `Cell.decimal`, `Cell.int`, `Cell.bool`, `Cell.duration`, `Cell.datetime`, `Cell.date`.

## [3.13.2] - 2024-12-15

-   Refactor Table and Row caching, removing useless `_caching` attribute from many classes.
-   Remove module scriptutils.

### Changed

-   Refactoring of Table and Row caching.
-   Replace in `container.py` and scripts `show.py` and `styles.py` the previous functions of scriptutils.

### Removed

-   `odfdo.scriptutils.py` removed.

## [3.13.1] - 2024-12-14

-   Allow XML export of base64 encoded images (preparing for flat ODF export).
-   Update XML propertires to ODF 1.2.

### Changed

-   Refactoring of Document.add_file() and export to XML format.

## [3.13.0] - 2024-12-07

-   The `Meta` class which manages the `meta.xml` part has two new methods `as_dict()` and `as_json()` to export its content.
-   Improved "pretty" export of documents.

### Added

-   Add methods: `Meta.as_dict()`, `Meta.as_json()`, `MetaTemplate.as_dict()`, `MetaAutoReload.as_dict()`, `MetaHyperlinkBehaviour.as_dict()`.

### Changed

-   Small XML file formatting changes when saving with "pretty=True".

## [3.12.1] - 2024-11-30

Fix some small rendering issues for Markdown export.

### Fixed

-   Better Markdown export for strike style, non break space, successive tags, line breaks, footnotes

## [3.12.0] - 2024-11-30

-   Change in `str(Paragraph)` which now includes a `'\n'` at the end of the string.
-   The `odfdo-to-md` script is renamed to `odfdo-markdown` and should be functional. Markdown export of .odt files supports all standard formatting features (including tables) except quoted text (no clear semantic equivalent in the ODF standard).
-   Improved `__str__` methods for many classes: Document.body, Paragraph, Span, Link, Unit, Note, Annotation.
-   Some added methods: `Document.get_parent_style()`, `Document.get_list_style()`, `Style.get_list_style_properties()`, `Style.get_text_properties()`.
-   The new `Element.inner_text` property is now the preferred way to access an element's inner text.

### Added

-   Add methods: `Document.get_parent_style()`, `Document.get_list_style()`, `Style.get_list_style_properties()`, `Style.get_text_properties()`.
-   Add propterty `Element.inner_text`.

### Changed

-   Script `odfdo-to-md` renamed to `odfdo-markdown`.
-   `str(Paragraph)` now includes a `'\n'` at the end of the string.
-   Output of the __str__ method modified for many elements.


## [3.11.0] - 2024-11-23

-   New script `odfdo-to-md` to export text document in markdown format to stdout (experimental, do not export images links neither tables).
-   Fix `VarTime` initialization: class can now be initialized without mandatory time argument.

### Added

-   Add script `odfdo-to-md`.

### Changed

-   `odfdo-folder` script now writes XML files with the "pretty" option by default.

### Fixed

-   Fix `VarTime` initialization.

## [3.10.1] - 2024-11-23

The HTML documentation in `/doc` (mostly auto generated) contains now all recipes, sorted by relevance.

### Changed

-   Improvement of documentation.

## [3.10.0] - 2024-11-23

-   Fix a bug of `Paragraph.set_span()` when using an offset argument of zero (the  Span was not created). Added 3 methods related to searching strings in paragraphs: `search_first()`, `search_all()` and `text_at()`. These methods permit to search some string with regex in a paragraph and get their position, `text_at()` returns the text content at a given position.
-   Fix the "pretty" option of `Document.save()`. "pretty" is now the default for odfdo-folder.

Added a new recipe showing several methods to change the style of a paragraph or words in a pragraph with the use of `Paragraph.style = style.name` and `Paragraph.set_span()`.

### Added

-   Added `Element.search_first()`, `Element.search_all()` , `Element.text_at()`.
-   Added `change_paragraph_styles_or_spans.py` recipe (issue #21).

### Changed

-   `odfdo-folder` script now writes XML files with the "pretty" option by default.

### Fixed

-   Fix `Paragraph.set_span()` when using an offset argument of zero (issue #21).
-   Fix the "pretty" option of `Document.save()` (issue #28).

## [3.9.4] - 2024-11-06

Fix a performance bug on huge .ods tables when number of rows is a large (several thousand).
See issue #46 for a table of about ~83k. Table.traverse() on such a table is expected to be ~2 sec.

### Changed

-   Rewrite the method Table.traverse().

### Fixed

-   Fix the performance bug on huge .ods tables (issue #46).

## [3.9.3] - 2024-10-14

Add support for Python 3.13 final in test suite.

### Added

-   Add support for Python3.13 in tox.ini

## [3.9.2] - 2024-10-05

Add support for Python 3.13.0.rc3 in test suite.

### Added

-   Add support for Python3.13.0.rc3 in tox.ini, add requirement for lxml version 5.3 or higher for Python 3.13.

## [3.9.1] - 2024-09-29

When creating a Document() allow alias "odt" for "Text", "ods" for "spreadsheet".

Add a recipe showing how to remove parts from a text document.

### Added

-   Aliases "odt", "ods", "odp" and "odg" for Document creation.

-   Add recipe `delete_parts_of_a_text_document.py`.

## [3.9.0] - 2024-09-22

Two changes in this version:

-    Fix of the broken `Table.displayed` property.
-    Fix the way spaces are represented for better compliance with the ODF standard and word processors.

The `Table.displayed` property was broken and is removed. The functionality is replaced by the `Document.get_table_displayed` and `Document.set_table_displayed` methods. This change should not affect anyone since the previous implementation was unusable.

In previous version 3 spaces were translated into 1 space followed by `'<text:s text:c="2"/>'` unconditionally. However, the standard specifies that at the beginning and end of a paragraph spaces must be discarded by word processors, so 3 spaces should be coded `'<text:s text:c="3"/>'` and a single space as `'<text:s/>'`. This change should fix the bug of "disappearing" spaces at the beginning of paragraphs.

### Added

-   Methods Document.get_table_displayed(), Document.set_table_displayed(), Document.get_table_style().

-   The Spacer() class has 2 new properties: Spacer.length and Spacer.text.

### Changed

-   XML generation of spaces at beginning and end of Paragraph content.

-   Update of dependency versions.

### Removed

-   Table.displayed property.

### Fixed

-   Fix the "disappearing" spaces at the beginning of paragraphs bug.

## [3.8.0] - 2024-08-25

Changed the default behavior for appending text to a `Paragraph`: the behavior of the `Paragraph.append_plain_text()` method is now the default. A `"formatted"` argument is added, `True` by default, which applies the recognition of "\n", "\t" or a sequence of several spaces and converts them to ODF tags (`text:line-break`, `text:tab`, `text:s`)). To ignore this text formatting, set `"formatted=False"`.

This change affects you if you create paragraphs from text containing line breaks or tabs and you don't want them to appear. In this case, add the argument `"formatted=False"`

Details:

- `Paragraph("word1     word2")`

    - previous behavior:
        - product XML:  `'<text:p>word1     word2</text:p>'`
        - expected display: `word1 word2` (single space, the ODF standard does not recognize space sequences)

    - new behavior:
        - product XML:  `'<text:p>word1 <text:s text:c="4"/>word2</text:p>'`
        - expected display: `word1     word2` (5 spaces)

- `Paragraph("word1     word2", formatted=False)`

    - new behavior:
        - product XML:  `'<text:p>word1 word2</text:p>'`
        - expected display: `word1 word2`

- `Paragraph("word1\nword2")`

    - previous behavior:
        - product XML:  `'<text:p>word1\nword2</text:p>'`
        - expected display: `word1 word2` (single space, the ODF standard does not recognize "\n" in XML content)

    - new behavior:
        - product XML:  `'<text:p>word1<text:line-break/>word2</text:p>'`
        - expected display:
            ```
            word1
            word2
            ```

- `Paragraph("word1\nword2", formatted=False)`

    - new behavior:
        - product XML:  `'<text:p>word1 word2</text:p>'`
        - expected display: `word1 word2`

On the same principle the `"formatted"` argument is available for `Pararaph.append(text)`, `Header(text)`, `Span(text)`.

The `Paragraph.append_plain_text(text)` method is retained for compatibility with previous versions and has the same behavior as `Paragraph.append(text, formatted=True)`, the default.

### Changed

-   `Paragraph()`, `Paragraph.append()` and subclasses `Header()` and `Span()` have a new `"formatted"` argument True by default that translates into ODF format "\n", "\t" and multiples spaces.

-   Updating dependency versions.

## [3.7.13] - 2024-08-17

-   Fix parsing of Date and Datetime for a better compliance with ISO8601.

### Changed

-   Updating dependency versions.

### Fixed

-   Fix datetime encoding/decoding for ISO8601 compliance and different Python versions.

-   Move from strptime() to date.isoformat() for class Date and DateTime.

## [3.7.12] - 2024-08-11

-   Update dependencies and test suite, support of `lxml` version 5.3.0.

### Changed

-   Updating dependency versions.

### Fixed

-   Fix a type hint in element.py

-   Fix missing .venv in gitconfig

## [3.7.11] - 2024-05-25

-   New script `odfdo-userfield` to show or set the user-field content in an ODF file.

### Added

-   Add script `odfdo-userfield`.

### Changed

-   Updating dependency versions.

## [3.7.10] - 2024-05-4

-   Refactor to add property getter for some common methods. Original get\_\*
    method is still available and permits detailed requests with parameters.

        -   Body.tables -> Body.get_tables()
        -   Element.tocs -> Element.get_tocs()
        -   Element.toc -> Element.get_toc()
        -   Element.text_changes -> Element.get_text_changes()
        -   Element.tracked_changes -> Element.get_tracked_changes()
        -   Element.user_defined_list -> Element.get_user_defined_list()
        -   Element.images -> Element.get_images()
        -   Element.frames -> Element.get_frames()
        -   Element.lists -> Element.get_lists()
        -   Element.headers -> Element.get_headers()
        -   Element.spans -> Element.get_spans()
        -   Element.paragraphs -> Element.get_paragraphs()
        -   Element.sections -> Element.get_sections()
        -   Table.rows -> Table.get_rows()
        -   Table.cells -> Table.get_cells()
        -   Table.columns -> Table.get_columns()
        -   Row.cells -> Row.get_cells()
        -   Document.parts -> Document.get_parts()
        -   Container.parts -> Container.get_parts()

-   Refactor to add property getter/setter for some common methods. Original get\_\*
    and set\_\* methods are still available and permit detailed requests with parameters.

        -   Column.default_cell_style -> Column.get/set_default_cell_style()

### Added

-   Added `Body.tables`
-   Added `Element.tocs`
-   Added `Element.toc`
-   Added `Element.text_changes`
-   Added `Element.tracked_changes`
-   Added `Element.images`
-   Added `Element.frames`
-   Added `Element.lists`
-   Added `Element.headers`
-   Added `Element.spans`
-   Added `Element.paragraphs`
-   Added `Element.sections`
-   Added `Column.default_cell_style`
-   Added `Table.rows`
-   Added `Table.cells`
-   Added `Table.columns`
-   Added `Row.cells`
-   Added `Document.parts`
-   Added `Container.parts`

## [3.7.9] - 2024-05-3

-   Refactor the Body access methods, creating relevant a Body class and related sub-classes. Moved some access method from the Element class to relevant Body sub-classes.

-   Refactor metadata methods to permit access throuh @property (the legacy get\_\* and set\_\* methods are still available).

-   Added a few metadata elements from the ODF standard (hyperlink-behaviour, auto-reload, template, print-dateprinted-by)

### Added

-   Added `MetaAutoReload` class
-   Added `MetaHyperlinkBehaviour` class
-   Added `MetaTemplate` class
-   Added `DcCreatorMixin` class
-   Added `DcDateMixin` class
-   Added `Body` class
-   Added `Chart` class
-   Added `Database` class
-   Added `Drawing` class
-   Added `Image` class
-   Added `Presentation` class
-   Added `Spreadsheet` class
-   Added `Text` class (renaming the previous internal `Text` class to `EText`)

## [3.7.8] - 2024-05-2

Fix embedded chart analysis in documents, see recipe `change_values_of_a_chart_inside_a_document.py`.

### Added

-   Added `change_values_of_a_chart_inside_a_document.py` recipe

### Changed

-   The "pretty" setting when saving the file always defaults to False. This setting should only be used for debugging purposes

-   `meta.generator` can be used via a @property accessor

-   (Internal change) move body() definition to xmlpart

-   (Internal change) refactoring for future XML feature

### Fixed

-   Fix parsing of Table when parent uses "table:table-rows" kind of wrapper

-   Fix a bug when a Cell contains the valid 'NaN' Decimal number

## [3.7.7] - 2024-04-1

Improvement of the `lxml` dependency support.

### Added

-   Added a `CHANGES.md` file

-   Automatic tests for ubuntu-latest, macos-latest, windows-latest

### Changed

-   Now supports a wider range of `lxml` versions:

    -   python 3.9: lxml version 4.8.0 to 4.9.4

    -   python 3.10: lxml version 4.8.0 to 5.1.1

    -   python 3.11: lxml version 4.9.4 to 5.2.0 and beyond

    -   python 3.12: lxml version 4.9.4 to 5.2.0 and beyond

-   autogenerated documentation now uses `mkdocs`

### Fixed

-   Use `sys.executable` to ensure all tests can pass in a github virtualenv on Windows.

-   Remove import of `lxml` internal `\_ElementUnicodeResult` and `\_ElementUnicodeResult` classes.

## [3.7.6] - 2024-03-30

Quick fix for the crash with new `lxml` version 5.1.1

### Fixed

    - Fix crash with `lxml` 5.1.1 by restricting version do 5.1.0

## [3.7.5] - 2024-03-23

Add the method `get_cell_background_color` to retrieve the background color of a cell in a table.

### Added

-   Tables: some users need to easily access the background color of cells, including cells without "value" content. That was requiring a complex parsing of styles. So a new method: `Document.get_cell_background_color(sheet_id, cell_coords)`.

-   See the corresponding recipe `recipes/get_cell_background_color.py` for an exemple of usage.

-   Tables: (related to previous). It is often useful to reduce the table size before working on it, especially if styles apply to whole rows. A method called `Table.rstrip()` already permitted to remove empty bottom rows and empty right columns. However, a `Cell` mays have no value but a style (color background for example), and `rstrip()` was removing such cells. So an new clever method is provided: `Table.optimize_width()` that shrink the table size, still keeping styled empty cells.

-   To test the actual result of this method, you can use the new script `odfdo-table-shrink` which is basically a wrapper upon this method. (Note: all this stuff aims to facilitate some feature for the related github project `odsparsator`).

-   `repr()` method for `Cell`, `Row` and `Column`.

-   Ancillary methods related to above features.

### Fixed

-   `Document(path)` now accepts a `str` path starting with `~` as the path relative to the user home.

### Changed

-   Tables: (related to previous), change the `Cell.is_empty()` test. A cell is now considered as not empty if part of a `span` (a cell spanned on several rows or columns). This may induce some changes for parsing scripts. Before that, only the first cell of the span (which actually contains the value) was considered as non empty. Now other cells of the span are not empty (but contain a null value).

-   Minor refactor of code, version updates of dependencies.

## [3.7.4] - 2024-03-17

Add a recipe as example of programmatically setting text styles for headers and paragraphs, with basic font and color properties.

### Added

-   Add recipe `create_basic_text_styles`.

-   All style fields related to color accept a color name from the CSS list of color.

### Changed

-   Updating dependency versions.

## [3.7.3] - 2024-03-10

Internal maintenance release.

### Fixed

-   Fix logo link on `Pypi` page.

### Changed

-   Technical updates from `optparse` to `argparse`.

-   Updating dependency versions.

## [3.7.2] - 2024-03-9

Internal maintenance release.

### Changed

-   Use `pdoc` for autogenerated documentation.

-   Refactor some recipes to use them in a test suit.

-   Code refactor, Updating dependency versions.

## [3.7.1] - 2024-03-3

Minor performance improvement of script `odfdo-headers`.

### Changed

-   Use better algorithm for script `odfdo-headers`.

## [3.7.0] - 2024-03-2

New script `odfdo-headers` to print the headers of a `ODF` file.

### Added

-   Add script `odfdo-headers`.

### Changed

-   Updating dependency versions.

## [3.6.0] - 2024-02-25

New script `odfdo-highlight` to highlight the text matching a pattern (regex) in a `ODF` file.

### Added

-   Add script `odfdo-highlight`.

### Changed

-   Updating dependency versions.

## [3.5.1] - 2024-02-20

Fix the update method of `Table of Content` and add a recipe to show how to update a `TOC`.

### Added

-   Add recipe `update_a_text_document_with_a_table_of_content`.

### Changed

-   Refactor of TOC related code.

-   Updating dependency versions.

## [3.5.0] - 2024-01-27

2024 release, updated ODF templates and better test suit.

### Changed

-   Update `ODF` templates.

-   Refactor many Python files for use of type hints.

-   Updates for year 2024, updating dependency versions.

## [3.4.7] - 2024-01-15

Updade to `lxml` version 5.

### Changed

    - Update `lxml` from version 4 to 5.

## [3.4.6] - 2023-12-25

Add script `odfdo-replace` to find a pattern (regex) in an `ODF` file and replace by some string.

### Fixed

-   Fix reading content from a `BytesIO`.

### Changed

-   Add script `odfdo-replace`.

## [3.4.5] - 2023-12-24

Add recipes showing how to save/read document from `io.BytesIO`.

### Added

-   Add recipes `read_document_from_bytesio.py` and `save_document_as_bytesio.py`.

### Changed

-   Refactoring of code.
