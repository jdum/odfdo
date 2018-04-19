# Copyright 2018 Jérôme Dumonteil
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

__all__ = (
    'Bookmark BookmarkStart BookmarkEnd Container Content Content '
    'Document DrawPage Element Text FIRST_CHILD LAST_CHILD NEXT_SIBLING '
    'PREV_SIBLING Frame default_frame_position_style Header DrawImage '
    'DrawFillImage Link ListItem List Manifest Meta Note Annotation '
    'AnnotationEnd Spacer Tab LineBreak Span Paragraph Reference '
    'ReferenceMark ReferenceMarkStart ReferenceMarkEnd Section '
    'ConnectorShape DrawGroup LineShape RectangleShape EllipseShape '
    'AnimPar AnimSeq AnimTransFilter default_boolean_style '
    'default_currency_style default_number_style default_percentage_style '
    'default_time_style default_date_style make_table_cell_border_string '
    'create_table_cell_style Style BackgroundImage rgb2hex hex2rgb Styles '
    'ChangeInfo TextInsertion TextDeletion TextFormatChange '
    'TextChangedRegion TrackedChanges TextChange TextChangeEnd '
    'TextChangeStart Cell Row Column Table HeaderRows RowGroup NamedRange '
    'IndexTitleTemplate default_toc_level_style TOC IndexTitle '
    'TocEntryTemplate TabStopStyle UserFieldDecl UserFieldGet '
    'UserFieldInput UserDefined VarChapter VarFileName VarInitialCreator '
    'VarCreationDate VarCreationTime VarDescription VarDecls VarDecl '
    'VarSet VarGet UserFieldDecls VarPageNumber VarPageCount VarDate '
    'VarTime VarTitle VarSubject VarKeywords XmlPart').split()

from .version import __version__
from .bookmark import Bookmark, BookmarkStart, BookmarkEnd
from .container import Container
from .content import Content
from .content import Content
from .document import Document
from .draw_page import DrawPage
from .element import Element, Text
from .element import FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING
from .frame import Frame, default_frame_position_style
from .header import Header
from .image import DrawImage, DrawFillImage
from .link import Link
from .list import ListItem, List
from .manifest import Manifest
from .meta import Meta
from .note import Note, Annotation, AnnotationEnd
from .paragraph import Spacer, Tab, LineBreak, Span, Paragraph
from .reference import Reference, ReferenceMark, ReferenceMarkStart
from .reference import ReferenceMarkEnd
from .section import Section
from .shapes import ConnectorShape, DrawGroup, LineShape, RectangleShape
from .shapes import EllipseShape
from .smil import AnimPar, AnimSeq, AnimTransFilter
from .style import default_boolean_style, default_currency_style
from .style import default_number_style, default_percentage_style
from .style import default_time_style, default_date_style
from .style import make_table_cell_border_string, create_table_cell_style
from .style import Style, BackgroundImage, rgb2hex, hex2rgb
from .styles import Styles
from .tracked_changes import ChangeInfo, TextInsertion, TextDeletion
from .tracked_changes import TextFormatChange, TextChangedRegion
from .tracked_changes import TrackedChanges, TextChange, TextChangeEnd
from .tracked_changes import TextChangeStart
from .table import Cell, Row, Column, Table, HeaderRows, RowGroup, NamedRange
from .toc import IndexTitleTemplate, default_toc_level_style
from .toc import TOC, IndexTitle, TocEntryTemplate, TabStopStyle
from .variable import UserFieldDecl, UserFieldGet, UserFieldInput, UserDefined
from .variable import VarChapter, VarFileName, VarInitialCreator
from .variable import VarCreationDate, VarCreationTime, VarDescription
from .variable import VarDecls, VarDecl, VarSet, VarGet, UserFieldDecls
from .variable import VarPageNumber, VarPageCount, VarDate, VarTime
from .variable import VarTitle, VarSubject, VarKeywords
from .xmlpart import XmlPart
