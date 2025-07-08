# Recipes

Recipes source code is in the `/recipes` directory of `odfdo` sources.
Most recipes are autonomous scripts doing actual modifications of ODF sample files, you can check the results in the `recipes/recipes_output` directory.

## How to write hello world in a text document

Create a minimal text document with "Hello World" in a pragraph.

??? code "recipes/how_to_write_hello_world_in_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_write_hello_world_in_a_text_document.py" %}
    ```

## How to write hello world in a spreadsheet document

Create a minimal spreadsheet with "Hello World" in the first cell.

??? code "recipes/how_to_write_hello_world_in_a_spreadsheet_document.py"
    ```python
    {% include "../../recipes/how_to_write_hello_world_in_a_spreadsheet_document.py" %}
    ```

## Basic presentation hello world

Write a basic "Hello World" in the middle of the first page
of a presentation.


??? code "recipes/basic_presentation_hello_world.py"
    ```python
    {% include "../../recipes/basic_presentation_hello_world.py" %}
    ```

## Create a basic text document

Create a basic text document with headers and praragraphs.

??? code "recipes/create_a_basic_text_document.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document.py" %}
    ```

## How to add a paragraph to a text document

Minimal example of how to add a paragraph.

??? code "recipes/how_to_add_a_paragraph_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_paragraph_to_a_text_document.py" %}
    ```

## Create a basic text document with a list

Create a basic text document with a list.

??? code "recipes/create_a_basic_text_document_with_a_list.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document_with_a_list.py" %}
    ```

## Create a basic text document with list and sublists

Create a short text document containing a list of items and a few sublists.
The code demonstrates several manipulations of the list and its items, then
displays the result to standard output.

??? code "recipes/create_a_basic_text_document_with_list_and_sublists.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document_with_list_and_sublists.py" %}
    ```

## How to add a sublist to a list

Minimal example of how to add a sublist to a list.

??? code "recipes/how_to_add_a_sublist_to_a_list.py"
    ```python
    {% include "../../recipes/how_to_add_a_sublist_to_a_list.py" %}
    ```

## How to add an item to a list

Minimal example of how to add an item to a list.

??? code "recipes/how_to_add_an_item_to_a_list.py"
    ```python
    {% include "../../recipes/how_to_add_an_item_to_a_list.py" %}
    ```

## How to insert a new item within a list

Minimal example of how to insert a new item within a list.

??? code "recipes/how_to_insert_a_new_item_within_a_list.py"
    ```python
    {% include "../../recipes/how_to_insert_a_new_item_within_a_list.py" %}
    ```

## Get text content from odt file

Read the text content from an .odt file.

??? code "recipes/get_text_content_from_odt_file.py"
    ```python
    {% include "../../recipes/get_text_content_from_odt_file.py" %}
    ```

## Create a basic text document with a table of content

Create a basic document containing some paragraphs and headers, add a
Table of Content from its headers.


??? code "recipes/create_a_basic_text_document_with_a_table_of_content.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document_with_a_table_of_content.py" %}
    ```

## Update a text document with a table of content

Update the table of contents of a document.

??? code "recipes/update_a_text_document_with_a_table_of_content.py"
    ```python
    {% include "../../recipes/update_a_text_document_with_a_table_of_content.py" %}
    ```

## Create a basic text document with annotations

Create a basic document containing some paragraphs and headers, add some
annotations. Annotations are notes that don't appear in the document but
typically on a side bar in a desktop application. So they are not printed.


??? code "recipes/create_a_basic_text_document_with_annotations.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document_with_annotations.py" %}
    ```

## Create a basic text document with footnotes

Create a basic document containing some paragraphs and headers, add some
footnotes. Footnotes are displayed at the end of the pages of the document.


??? code "recipes/create_a_basic_text_document_with_footnotes.py"
    ```python
    {% include "../../recipes/create_a_basic_text_document_with_footnotes.py" %}
    ```

## How to add footnote to a text document

Minimal example of how to add an footnote to a text document.

Notes are quite complex so they deserve a dedicated API on paragraphs:

paragraph.insert_note()

The arguments are:

after    =>   The word after what the “¹” citation is inserted.
note_id  =>	  A unique identifier of the note in the document.
citation =>   The symbol the user sees to follow the footnote.
body 	 =>   The footnote itself, at the end of the page.

odfdo creates footnotes by default. To create endnotes (notes
that appear at the end of the document), add the parameter:
note_class='endnote'.


??? code "recipes/how_to_add_footnote_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_footnote_to_a_text_document.py" %}
    ```

## Create a text document with tables in it

Build a commercial document, with numerical values displayed in
both the text and in a table.


??? code "recipes/create_a_text_document_with_tables_in_it.py"
    ```python
    {% include "../../recipes/create_a_text_document_with_tables_in_it.py" %}
    ```

## How to add a table to a document

Minimal example of how to add a table to a text document.

??? code "recipes/how_to_add_a_table_to_a_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_table_to_a_document.py" %}
    ```

## Create a text document from plain text with layout

Create a text document with custom styles. In this recipe, the styles
are created from their XML definition.

Steps:

 - Remove standard styles from the document,

 - set some styles grabed from a styles.xml ODF file (or generated),

 - insert plain "python" text, containing some 	 , 
, and spaces.


??? code "recipes/create_a_text_document_from_plain_text_with_layout.py"
    ```python
    {% include "../../recipes/create_a_text_document_from_plain_text_with_layout.py" %}
    ```

## Add a custom footer to a text document

Minimal example of setting a page footer using Style.set_page_footer().

Note: the created footer uses the current footer style, to change that
footer style, use the method  set_footer_style() on the 'page-layout'
style family.


??? code "recipes/add_a_custom_footer_to_a_text_document.py"
    ```python
    {% include "../../recipes/add_a_custom_footer_to_a_text_document.py" %}
    ```

## How to add a picture to a text document

Create an empty text document and add a picture in a frame.


??? code "recipes/how_to_add_a_picture_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_picture_to_a_text_document.py" %}
    ```

## How to add a right aligned picture to a text document

Create an empty text document and add a picture in a frame,
aligned to the right or to the left.

Aligning an image requires applying a style to the frame. To do
this, use the default frame position style and customize it. The
frame position style allows you to choose alignment relative to
the paragraph (default) or the page.


??? code "recipes/how_to_add_a_right_aligned_picture_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_right_aligned_picture_to_a_text_document.py" %}
    ```

## How to add a title to a text document

Minimal example of how to add a Header of first level to a text document.

??? code "recipes/how_to_add_a_title_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_title_to_a_text_document.py" %}
    ```

## Accessing a single element

Example of methods and properties to analyse a document.

These methods return a single element (or None):

    - `body.get_note(position)`
    - `body.get_paragraph(position)`
    - `body.get_header(position)`


??? code "recipes/accessing_a_single_element.py"
    ```python
    {% include "../../recipes/accessing_a_single_element.py" %}
    ```

## Accessing a list of elements

Example of methods and properties to analyse a document.

These methods or properties return a list of elements:

    - `body.headers`
    - `body.images`
    - `body.paragraphs`
    - `body.get_links()`
    - `body.get_notes()`
    - `body.tables`
    - `body.get_paragraphs(content)`


??? code "recipes/accessing_a_list_of_elements.py"
    ```python
    {% include "../../recipes/accessing_a_list_of_elements.py" %}
    ```

## Accessing other element from element like list

Accessing elements from element-like list.

Any fetched element is a XML tree context that can be queried, but only on the subtree it
contains. Here are quick examples of iteration on `Paragraphs` and `Lists` from the document.


??? code "recipes/accessing_other_element_from_element_like_list.py"
    ```python
    {% include "../../recipes/accessing_other_element_from_element_like_list.py" %}
    ```

## How to add a list to a text document

Create an empty text document and add a list.

??? code "recipes/how_to_add_a_list_to_a_text_document.py"
    ```python
    {% include "../../recipes/how_to_add_a_list_to_a_text_document.py" %}
    ```

## How to add a manual page break

Adding a manual page break to a text document.

Page breaks are build by a specific style. However, odfdo provides a PageBreak
class to facilitate the inclusion of page breaks. This recipe illustrates
the use of PageBreak and the underlying styling mechanism.


??? code "recipes/how_to_add_a_manual_page_break.py"
    ```python
    {% include "../../recipes/how_to_add_a_manual_page_break.py" %}
    ```

## Create a basic drawing

Insert a circle and a lot of lines (a fractal) in a text document.

??? code "recipes/create_a_basic_drawing.py"
    ```python
    {% include "../../recipes/create_a_basic_drawing.py" %}
    ```

## Add private annotations to a document

Add not printable annotations to a document.

Annotations are notes that do not appear in the document but typically
on a side bar in a desktop application. So they are not printed.


??? code "recipes/add_private_annotations_to_a_document.py"
    ```python
    {% include "../../recipes/add_private_annotations_to_a_document.py" %}
    ```

## Accessibility check on a document

Basic Accessibility test: check, for every picture in a document, if
there is:

  - a title (svg_title),
  - a description (svg_description)

or, at least, some caption text.

See test file `planes.odt` file and the result of the script.


??? code "recipes/accessibility_check_on_a_document.py"
    ```python
    {% include "../../recipes/accessibility_check_on_a_document.py" %}
    ```

## Add logo on presentation

Insert an image (e.g. the logo of an event, organization or a Creative Commons
attribution) with size `x,y` at position `x2,y2` on a number of slides in a
presentation slide deck.


??? code "recipes/add_logo_on_presentation.py"
    ```python
    {% include "../../recipes/add_logo_on_presentation.py" %}
    ```

## Get pictures from document odt

Retrieve all the pictures embeded in an .odt file.

??? code "recipes/get_pictures_from_document_odt.py"
    ```python
    {% include "../../recipes/get_pictures_from_document_odt.py" %}
    ```

## Change image in many documents

Change an image in many ODF files.

This recipe is suitable for the scenario where an organization
is moving from one company logo to another and needs to replace
the logo in several hundred existing documents.


??? code "recipes/change_image_in_many_documents.py"
    ```python
    {% include "../../recipes/change_image_in_many_documents.py" %}
    ```

## Concatenate presentations

Concatenate several presentations (including presentations found in sub
directories), possibly merge styles and images. Result for style may vary.


??? code "recipes/concatenate_presentations.py"
    ```python
    {% include "../../recipes/concatenate_presentations.py" %}
    ```

## Make a presentation from pictures of a text document

Open a .odt file with pictures in it, find and analyse all the images,
create a new .odp presentation, display all the pictures in the presentation,
one image per frame.


??? code "recipes/make_a_presentation_from_pictures_of_a_text_document.py"
    ```python
    {% include "../../recipes/make_a_presentation_from_pictures_of_a_text_document.py" %}
    ```

## Make presentation from images

Create a presentation from a some images in a given directory,
where each image is put on the center of its own page scaled to either
the maximum available size, prefered maximum size, or cover the full
page and lose some info.


??? code "recipes/make_presentation_from_images.py"
    ```python
    {% include "../../recipes/make_presentation_from_images.py" %}
    ```

## Make a presentation from text with different styles

Each line of the text becomes a slide of the presentation, we change of style
depending on the length of text line.


??? code "recipes/make_a_presentation_from_text_with_different_styles.py"
    ```python
    {% include "../../recipes/make_a_presentation_from_text_with_different_styles.py" %}
    ```

## Extract and reorder slides

Create a new presentation from a previous one by extracting some slides,
in a different order.


??? code "recipes/extract_and_reorder_slides.py"
    ```python
    {% include "../../recipes/extract_and_reorder_slides.py" %}
    ```

## Change values of a chart inside a document

Open a text document with an embedded chart and change some values.

??? code "recipes/change_values_of_a_chart_inside_a_document.py"
    ```python
    {% include "../../recipes/change_values_of_a_chart_inside_a_document.py" %}
    ```

## Add text span styles

Transform a not styled document into a multi styled document,
by changing size and color of each parts of words.


??? code "recipes/add_text_span_styles.py"
    ```python
    {% include "../../recipes/add_text_span_styles.py" %}
    ```

## How to copy some style from another document

Minimal example of copy of a style from another document.

Document.get_style() main parameters:
family        : The family of the style, text styles apply on individual
                characters.
display_name  : The name of the style as we see it in a desktop
                application. Styles have an internal name
                (“Yellow_20_Highlight” in this example) but here we use
                the display_name instead.


??? code "recipes/how_to_copy_some_style_from_another_document.py"
    ```python
    {% include "../../recipes/how_to_copy_some_style_from_another_document.py" %}
    ```

## Copy style from another document

Copy the styles from an existing document.

For more advanced version, see the odfdo-style script.


??? code "recipes/copy_style_from_another_document.py"
    ```python
    {% include "../../recipes/copy_style_from_another_document.py" %}
    ```

## Create basic text styles

Create basic text styles with the Style class API.

Styles are applied to entire paragraphs or headings, or to words using Span.

The create_style_steel() and create_style_special() functions below are
examples of styles that combine the area="text" and area="Graphic" or
area="paragraph" properties. The Style class API allows for basic styling,
but for more complex situations, it is recommended to use a document as a
template or copy the XML definition of an existing style. The recipe
change_paragraph_styles_methods.py shows these different methods.


??? code "recipes/create_basic_text_styles.py"
    ```python
    {% include "../../recipes/create_basic_text_styles.py" %}
    ```

## How to apply a style to a paragraph

Minimal example of how to add a styled paragraph to a document.

??? code "recipes/how_to_apply_a_style_to_a_paragraph.py"
    ```python
    {% include "../../recipes/how_to_apply_a_style_to_a_paragraph.py" %}
    ```

## Change paragraph styles methods

Many examples of how to change paragraph (and in-paragraph) styles, either
by changing the paragraph style itself or by using Span to select parts
of the paragraph. Includes several ways to create or import styles.


??? code "recipes/change_paragraph_styles_methods.py"
    ```python
    {% include "../../recipes/change_paragraph_styles_methods.py" %}
    ```

## Delete parts of a text document

Deleting content from one point to another in a .odt document.

(Idea from an answer to problem #49).


??? code "recipes/delete_parts_of_a_text_document.py"
    ```python
    {% include "../../recipes/delete_parts_of_a_text_document.py" %}
    ```

## Create color chart in spreadsheet

Create some color chart in a spreadsheet using cells styles functions.

For cells, use of functions:
    make_table_cell_border_string()
    create_table_cell_style()
    rgb2hex()

Apply a row style to define the row height.

Apply a column style to define the column width.


??? code "recipes/create_color_chart_in_spreadsheet.py"
    ```python
    {% include "../../recipes/create_color_chart_in_spreadsheet.py" %}
    ```

## Get cell background color

Read the background color of a table cell.

??? code "recipes/get_cell_background_color.py"
    ```python
    {% include "../../recipes/get_cell_background_color.py" %}
    ```

## Extract a sub table from some big table

Open a table of 1000 lines and 100 columns, extract a sub table
of 100 lines 26 columns, save the result in a spreadsheet document.


??? code "recipes/extract_a_sub_table_from_some_big_table.py"
    ```python
    {% include "../../recipes/extract_a_sub_table_from_some_big_table.py" %}
    ```

## Make a basic spreadsheet

Create a spreadsheet with one table and a few data, strip the table
and compute the table size.


??? code "recipes/make_a_basic_spreadsheet.py"
    ```python
    {% include "../../recipes/make_a_basic_spreadsheet.py" %}
    ```

## Make spreadsheet with named ranges

Create a spreadsheet with two tables, using named ranges to fill cells.

??? code "recipes/make_spreadsheet_with_named_ranges.py"
    ```python
    {% include "../../recipes/make_spreadsheet_with_named_ranges.py" %}
    ```

## Introspecting elements

Demo of quick introspecting of a document's elements.

The body object of a document is a mapping of an XML tree from which we
can access other elements we are looking for (parent, children).

??? code "recipes/introspecting_elements.py"
    ```python
    {% include "../../recipes/introspecting_elements.py" %}
    ```

## Show meta data

Print the metadata informations of a ODF file.

Metadata are accessible through the meta part: meta = document.get_part("meta.xml")
or the shortcut: document.meta.

You then get access to various getters and setters. The getters return
Python types and the respective setters take the same Python type as
a parameter.


??? code "recipes/show_meta_data.py"
    ```python
    {% include "../../recipes/show_meta_data.py" %}
    ```

## Move link to footnote

Remove all links from a document, transforming each link information (URL,
text) into a footnote. Of course, removing links already inside notes, just
keeping plain text URL. (Side note: most office suite dislike notes in notes)


??? code "recipes/move_link_to_footnote.py"
    ```python
    {% include "../../recipes/move_link_to_footnote.py" %}
    ```

## Remove http links

Remove all the links (the text:a tag), keeping the inner text.

??? code "recipes/remove_http_links.py"
    ```python
    {% include "../../recipes/remove_http_links.py" %}
    ```

## Remove span styles

Remove span styles (like some words in bold in a paragraph),
except in titles.


??? code "recipes/remove_span_styles.py"
    ```python
    {% include "../../recipes/remove_span_styles.py" %}
    ```

## Retrieve all pictures from odf files

Scan a list of files and directories (recursion), open all ODF documents
and copy document images to a target directory.


??? code "recipes/retrieve_all_pictures_from_ODF_files.py"
    ```python
    {% include "../../recipes/retrieve_all_pictures_from_ODF_files.py" %}
    ```

## Read document from bytesio

Read a document from BytesIO.

??? code "recipes/read_document_from_bytesio.py"
    ```python
    {% include "../../recipes/read_document_from_bytesio.py" %}
    ```

## Save document as bytesio

Save a document as BytesIO.

??? code "recipes/save_document_as_bytesio.py"
    ```python
    {% include "../../recipes/save_document_as_bytesio.py" %}
    ```

## Export tables to csv format

Export tables to CSV format.

??? code "recipes/export_tables_to_csv_format.py"
    ```python
    {% include "../../recipes/export_tables_to_csv_format.py" %}
    ```

## Import csv content into a table

Import a CSV file and load data into a table.

??? code "recipes/import_csv_content_into_a_table.py"
    ```python
    {% include "../../recipes/import_csv_content_into_a_table.py" %}
    ```

## Search and replace words

Search and replace words in a text document.

??? code "recipes/search_and_replace_words.py"
    ```python
    {% include "../../recipes/search_and_replace_words.py" %}
    ```

## Spreadsheet with words frequency from a text

Load an ODF text, store the frequency of words in a spreadsheet,
make requests on the table, by regex or value.


??? code "recipes/spreadsheet_with_words_frequency_from_a_text.py"
    ```python
    {% include "../../recipes/spreadsheet_with_words_frequency_from_a_text.py" %}
    ```

## Transpose table

Transpose a table. Create a spreadsheet table (for example: 50 rows and
20 columns), then create a new table in a separate sheet where the columns
and rows are swapped (for example: 20 rows and 50 columns).


??? code "recipes/transpose_table.py"
    ```python
    {% include "../../recipes/transpose_table.py" %}
    ```

