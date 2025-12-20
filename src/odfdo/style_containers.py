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
"""Classes for styles containers."""

from .element import Element, register_element_class
from .page_layout import StylePageLayout


class OfficeAutomaticStyles(Element):
    """Container for automatic styles used in the document, "office:automatic-styles".

    An automatic style contains formatting properties that are considered to
    be properties of the object to which the style is assigned.

    This element is usable within "office:document", "office:document-content",
    and "office:document-styles" elements, and has no attributes.
    """

    _tag: str = "office:automatic-styles"

    @property
    def page_layouts(self) -> list[StylePageLayout]:
        """Return the list of StylePageLayout styles.

        Returns:
            A list of StylePageLayout elements.
        """
        return [e for e in self.children if isinstance(e, StylePageLayout)]


class OfficeMasterStyles(Element):
    """Container for master styles used in the document, "office:master-styles".

    A master style contains formatting and other content that is displayed with
    document content when the style is used.

    This element is usable within "office:document" and "office:document-styles"
    elements, and has no attributes.
    """

    _tag: str = "office:master-styles"


register_element_class(OfficeAutomaticStyles)
register_element_class(OfficeMasterStyles)
