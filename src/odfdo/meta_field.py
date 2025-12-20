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
"""TextMeta and MetaField class for "text:meta" and "text:meta-field" tags."""

from __future__ import annotations

from .annotation import AnnotationMixin
from .bookmark import BookmarkMixin
from .element import register_element_class
from .mixin_link import LinkMixin
from .note import NoteMixin
from .reference import ReferenceMixin
from .user_field import UserDefinedMixin


class MetaField(
    UserDefinedMixin,
    LinkMixin,
    ReferenceMixin,
    BookmarkMixin,
    AnnotationMixin,
    NoteMixin,
):
    """Content from a metadata source.

    The mixed content of this element should be generated from the metadata
    source. The source of the metadata and the means of generation of the
    mixed content is implementation-dependent. The "text:meta-field" element
    may contain any paragraph content.
    """

    _tag = "text:meta-field"


class TextMeta(
    UserDefinedMixin,
    LinkMixin,
    ReferenceMixin,
    BookmarkMixin,
    AnnotationMixin,
    NoteMixin,
):
    """Represents portions of text that have in content metadata attached."""

    _tag = "text:meta"


register_element_class(MetaField)
register_element_class(TextMeta)
