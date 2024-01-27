# Copyright 2018-2024 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""Python library for OpenDocument Format (ODF)"""

__all__ = [
    "AnimPar",
    "AnimSeq",
    "AnimTransFilter",
    "Annotation",
    "AnnotationEnd",
    "BackgroundImage",
    "Bookmark",
    "BookmarkEnd",
    "BookmarkStart",
    "Cell",
    "ChangeInfo",
    "Column",
    "ConnectorShape",
    "Container",
    "Content",
    "Content",
    "Document",
    "DrawFillImage",
    "DrawGroup",
    "DrawImage",
    "DrawPage",
    "Element",
    "ElementTyped",
    "EllipseShape",
    "FIRST_CHILD",
    "Frame",
    "Header",
    "HeaderRows",
    "IndexTitle",
    "IndexTitleTemplate",
    "LAST_CHILD",
    "LineBreak",
    "LineShape",
    "Link",
    "List",
    "ListItem",
    "Manifest",
    "Meta",
    "NEXT_SIBLING",
    "NamedRange",
    "Note",
    "PREV_SIBLING",
    "Paragraph",
    "PageBreak",
    "RectangleShape",
    "Reference",
    "ReferenceMark",
    "ReferenceMarkEnd",
    "ReferenceMarkStart",
    "Row",
    "RowGroup",
    "Section",
    "Spacer",
    "Span",
    "Style",
    "Styles",
    "TOC",
    "Tab",
    "TabStopStyle",
    "Table",
    "Text",
    "TextChange",
    "TextChangeEnd",
    "TextChangeStart",
    "TextChangedRegion",
    "TextDeletion",
    "TextFormatChange",
    "TextInsertion",
    "TocEntryTemplate",
    "TrackedChanges",
    "UserDefined",
    "UserFieldDecl",
    "UserFieldDecls",
    "UserFieldGet",
    "UserFieldInput",
    "VarChapter",
    "VarCreationDate",
    "VarCreationTime",
    "VarDate",
    "VarDecl",
    "VarDecls",
    "VarDescription",
    "VarFileName",
    "VarGet",
    "VarInitialCreator",
    "VarKeywords",
    "VarPageCount",
    "VarPageNumber",
    "VarSet",
    "VarSubject",
    "VarTime",
    "VarTitle",
    "XmlPart",
    "__version__",
    "create_table_cell_style",
    "default_boolean_style",
    "default_currency_style",
    "default_date_style",
    "default_frame_position_style",
    "default_number_style",
    "default_percentage_style",
    "default_time_style",
    "default_toc_level_style",
    "hex2rgb",
    "make_table_cell_border_string",
    "rgb2hex",
]


from .bookmark import Bookmark, BookmarkEnd, BookmarkStart
from .container import Container
from .content import Content
from .document import Document
from .draw_page import DrawPage
from .element import FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING, Element, Text
from .element_typed import ElementTyped
from .frame import Frame, default_frame_position_style
from .header import Header
from .image import DrawFillImage, DrawImage
from .link import Link
from .list import List, ListItem
from .manifest import Manifest
from .meta import Meta
from .note import Annotation, AnnotationEnd, Note
from .paragraph import LineBreak, PageBreak, Paragraph, Spacer, Span, Tab
from .reference import Reference, ReferenceMark, ReferenceMarkEnd, ReferenceMarkStart
from .section import Section
from .shapes import ConnectorShape, DrawGroup, EllipseShape, LineShape, RectangleShape
from .smil import AnimPar, AnimSeq, AnimTransFilter
from .style import (
    BackgroundImage,
    Style,
    create_table_cell_style,
    default_boolean_style,
    default_currency_style,
    default_date_style,
    default_number_style,
    default_percentage_style,
    default_time_style,
    hex2rgb,
    make_table_cell_border_string,
    rgb2hex,
)
from .styles import Styles
from .table import Cell, Column, HeaderRows, NamedRange, Row, RowGroup, Table
from .toc import (
    TOC,
    IndexTitle,
    IndexTitleTemplate,
    TabStopStyle,
    TocEntryTemplate,
    default_toc_level_style,
)
from .tracked_changes import (
    ChangeInfo,
    TextChange,
    TextChangedRegion,
    TextChangeEnd,
    TextChangeStart,
    TextDeletion,
    TextFormatChange,
    TextInsertion,
    TrackedChanges,
)
from .variable import (
    UserDefined,
    UserFieldDecl,
    UserFieldDecls,
    UserFieldGet,
    UserFieldInput,
    VarChapter,
    VarCreationDate,
    VarCreationTime,
    VarDate,
    VarDecl,
    VarDecls,
    VarDescription,
    VarFileName,
    VarGet,
    VarInitialCreator,
    VarKeywords,
    VarPageCount,
    VarPageNumber,
    VarSet,
    VarSubject,
    VarTime,
    VarTitle,
)
from .version import __version__
from .xmlpart import XmlPart
