# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Classes related to "style:page-layout"."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .style_base import StyleBase


class StylePageLayout(StyleBase):
    """The "style:page-layout" element represents the styles that specify the formatting properties of a page.

    The "style:page-layout" element is usable within the following element:
    "office:automatic-styles".
    """

    # The "style:page-layout" element has the following attributes:
    # style:name
    # style:page-usage

    _tag: str = "style:page-layout"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "style:name"),
        PropDef("page_usage", "style:page-usage"),
    )

    def __init__(
        self,
        name: str | None = None,
        page_usage: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a StylePageLayout.

        The name is not mandatory at this point but will become required when inserting in a document as a automatic style.

        The page_usage attribute specifies the type of pages that a page master should generate. Allowed values are: "all" (default), "left", "mirrored", "right".

        To set properties, pass them as keyword arguments.

        Args:

            name -- str

            page_usage -- str
        """
        self._family = "page-layout"
        tag_or_elem = kwargs.get("tag_or_elem")
        if tag_or_elem is None:
            kwargs["tag"] = "style:page-layout"
        Element.__init__(self, **kwargs)
        if self._do_init:
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            if name:
                self.name = name
            if page_usage:
                self.page_usage = page_usage

    @property
    def family(self) -> str | None:
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family} name={self.name}>"

    @property
    def page_usage(self) -> str:
        return self._get_attribute_str_default("style:page-usage", "all")

    @page_usage.setter
    def page_usage(self, page_usage: str | None) -> None:
        self._set_attribute_str_default("style:page-usage", page_usage, "all")


StylePageLayout._define_attribut_property()


register_element_class(StylePageLayout)
