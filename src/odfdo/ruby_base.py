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
"""RubyBase class for "text:ruby-base" tag."""

from __future__ import annotations

from .annotation import AnnotationMixin
from .bookmark import BookmarkMixin
from .element import register_element_class
from .note import NoteMixin
from .reference import ReferenceMixin


class RubyBase(ReferenceMixin, BookmarkMixin, AnnotationMixin, NoteMixin):
    """Content the text that is to be annotated.

    It contains any paragraph element content, like text spans.
    The element's text:style-name attribute references a ruby
    style that specifies formatting attributes of the ruby.
    """

    _tag = "text:ruby-base"


register_element_class(RubyBase)
