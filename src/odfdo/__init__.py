# Copyright 2018-2025 Jérôme Dumonteil
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

__all__ = [  # noqa: RUF022
    "AnimPar",
    "AnimSeq",
    "AnimTransFilter",
    "Annotation",
    "AnnotationEnd",
    "AnnotationMixin",
    "BackgroundImage",
    "Body",
    "Bookmark",
    "BookmarkEnd",
    "BookmarkMixin",
    "BookmarkStart",
    "Cell",
    "ChangeInfo",
    "Chart",
    "Column",
    "ConnectorShape",
    "Container",
    "Content",
    "Database",
    "DcCreatorMixin",
    "DcDateMixin",
    "Document",
    "DrawFillImage",
    "DrawGroup",
    "DrawImage",
    "DrawPage",
    "DrawTextBox",
    "Drawing",
    "EText",
    "Element",
    "ElementTyped",
    "EllipseShape",
    "FIRST_CHILD",
    "Form",
    "FormAsDictMixin",
    "FormButton",
    "FormButtonTypeMixin",
    "FormButtonTypeMixin",
    "FormCheckbox",
    "FormColumn",
    "FormCombobox",
    "FormDate",
    "FormDelayRepeatMixin",
    "FormFile",
    "FormFixedText",
    "FormFormattedText",
    "FormFrame",
    "FormGenericControl",
    "FormGrid",
    "FormHidden",
    "FormImage",
    "FormImageAlignMixin",
    "FormImageFrame",
    "FormImagePositionMixin",
    "FormItem",
    "FormListProperty",
    "FormListValue",
    "FormListbox",
    "FormMaxLengthMixin",
    "FormMixin",
    "FormNumber",
    "FormOption",
    "FormPassword",
    "FormProperties",
    "FormProperty",
    "FormRadio",
    "FormSizetMixin",
    "FormSourceListMixin",
    "FormText",
    "FormTextarea",
    "FormTime",
    "FormValueRange",
    "Frame",
    "Header",
    "HeaderRows",
    "Image",
    "IndexBody",
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
    "MetaAutoReload",
    "MetaField",
    "MetaHyperlinkBehaviour",
    "MetaTemplate",
    "MetaUserDefined",
    "Metadata",
    "NEXT_SIBLING",
    "NRMixin",
    "NamedRange",
    "Note",
    "NoteBody",
    "NoteMixin",
    "OfficeAutomaticStyles",
    "OfficeForms",
    "OfficeFormsMixin",
    "OfficeMasterStyles",
    "OfficeTargetFrameMixin",
    "PREV_SIBLING",
    "PageBreak",
    "ParaMixin",
    "Paragraph",
    "Presentation",
    "PresentationNotes",
    "RectangleShape",
    "Reference",
    "ReferenceMark",
    "ReferenceMarkEnd",
    "ReferenceMarkStart",
    "ReferenceMixin",
    "Row",
    "RowGroup",
    "RubyBase",
    "Section",
    "SectionMixin",
    "Spacer",
    "Span",
    "Spreadsheet",
    "Style",
    "StyleFooter",
    "StyleFooterFirst",
    "StyleFooterLeft",
    "StyleHeader",
    "StyleHeaderFirst",
    "StyleHeaderLeft",
    "StyleMasterPage",
    "StylePageLayout",
    "Styles",
    "TOC",
    "Tab",
    "TabStopStyle",
    "Table",
    "TableNamedExpressions",
    "Text",
    "TextChange",
    "TextChangeEnd",
    "TextChangeStart",
    "TextChangedRegion",
    "TextDeletion",
    "TextFormatChange",
    "TextInsertion",
    "TextMeta",
    "TocEntryTemplate",
    "TocMixin",
    "TrackedChanges",
    "TrackedChangesMixin",
    "UserDefined",
    "UserDefinedMixin",
    "UserFieldDecl",
    "UserFieldDeclContMixin",
    "UserFieldDeclMixin",
    "UserFieldDecls",
    "UserFieldGet",
    "UserFieldInput",
    "VarChapter",
    "VarCreationDate",
    "VarCreationTime",
    "VarDate",
    "VarDecl",
    "VarDeclMixin",
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
    "hexa_color",
    "make_table_cell_border_string",
    "remove_tree",
    "rgb2hex",
]


from .annotation import Annotation, AnnotationEnd, AnnotationMixin
from .body import (
    Body,
    Chart,
    Database,
    Drawing,
    Image,
    Metadata,
    Presentation,
    Spreadsheet,
    Text,
)
from .bookmark import Bookmark, BookmarkEnd, BookmarkMixin, BookmarkStart
from .cell import Cell
from .column import Column
from .container import Container
from .content import Content
from .document import Document
from .draw_page import DrawPage
from .element import FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING, Element, EText
from .element_typed import ElementTyped
from .form import Form, FormMixin
from .form_controls import (
    FormButton,
    FormCheckbox,
    FormColumn,
    FormCombobox,
    FormDate,
    FormFile,
    FormFixedText,
    FormFormattedText,
    FormFrame,
    FormGenericControl,
    FormGrid,
    FormHidden,
    FormImage,
    FormImageFrame,
    FormItem,
    FormListbox,
    FormNumber,
    FormOption,
    FormPassword,
    FormRadio,
    FormText,
    FormTextarea,
    FormTime,
    FormValueRange,
)
from .form_controls_mixins import (
    FormAsDictMixin,
    FormButtonTypeMixin,
    FormDelayRepeatMixin,
    FormImageAlignMixin,
    FormImagePositionMixin,
    FormMaxLengthMixin,
    FormSizetMixin,
    FormSourceListMixin,
    OfficeTargetFrameMixin,
)
from .form_properties import (
    FormListProperty,
    FormListValue,
    FormProperties,
    FormProperty,
)
from .frame import DrawTextBox, Frame, default_frame_position_style
from .header import Header
from .header_rows import HeaderRows
from .image import DrawFillImage, DrawImage
from .line_break import LineBreak
from .link import Link
from .list import List, ListItem
from .manifest import Manifest
from .master_page import (
    StyleFooter,
    StyleFooterFirst,
    StyleFooterLeft,
    StyleHeader,
    StyleHeaderFirst,
    StyleHeaderLeft,
    StyleMasterPage,
)
from .meta import Meta
from .meta_auto_reload import MetaAutoReload
from .meta_field import MetaField, TextMeta
from .meta_hyperlink_behaviour import MetaHyperlinkBehaviour
from .meta_template import MetaTemplate
from .meta_user_defined import MetaUserDefined
from .mixin_dc_creator import DcCreatorMixin
from .mixin_dc_date import DcDateMixin
from .mixin_named_range import NRMixin, TableNamedExpressions
from .mixin_paragraph import ParaMixin
from .mixin_toc import TocMixin
from .named_range import NamedRange
from .note import Note, NoteBody, NoteMixin
from .office_forms import OfficeForms, OfficeFormsMixin
from .page_layout import StylePageLayout
from .paragraph import PageBreak, Paragraph, Span
from .presentation_notes import PresentationNotes
from .reference import (
    Reference,
    ReferenceMark,
    ReferenceMarkEnd,
    ReferenceMarkStart,
    ReferenceMixin,
)
from .row import Row
from .row_group import RowGroup
from .ruby_base import RubyBase
from .section import Section, SectionMixin
from .shapes import ConnectorShape, DrawGroup, EllipseShape, LineShape, RectangleShape
from .smil import AnimPar, AnimSeq, AnimTransFilter
from .spacer import Spacer
from .style import (
    BackgroundImage,
    Style,
    create_table_cell_style,
    make_table_cell_border_string,
)
from .style_containers import OfficeAutomaticStyles, OfficeMasterStyles
from .style_defaults import (
    default_boolean_style,
    default_currency_style,
    default_date_style,
    default_number_style,
    default_percentage_style,
    default_time_style,
)
from .styles import Styles
from .tab import Tab
from .table import Table
from .toc import (
    TOC,
    IndexBody,
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
    TrackedChangesMixin,
)
from .user_field import UserDefined, UserDefinedMixin, UserFieldGet, UserFieldInput
from .user_field_declaration import (
    UserFieldDecl,
    UserFieldDeclContMixin,
    UserFieldDeclMixin,
    UserFieldDecls,
)
from .utils import hex2rgb, hexa_color, remove_tree, rgb2hex
from .variable import (
    VarChapter,
    VarCreationDate,
    VarCreationTime,
    VarDate,
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
from .variable_declaration import VarDecl, VarDeclMixin, VarDecls
from .version import __version__
from .xmlpart import XmlPart
