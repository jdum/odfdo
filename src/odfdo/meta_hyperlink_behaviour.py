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
"""MetaHyperlinkBehaviour class for "meta:hyperlink-behaviour" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


class MetaHyperlinkBehaviour(Element):
    """Container for hyperlink-behaviour properties, "meta:hyperlink-behaviour"."""

    _tag = "meta:hyperlink-behaviour"
    _properties: tuple[PropDef, ...] = (
        PropDef("target_frame_name", "office:target-frame-name"),
        PropDef("show", "xlink:show"),
    )

    def __init__(
        self,
        target_frame_name: str = "_blank",
        show: str = "replace",
        **kwargs: Any,
    ) -> None:
        """
        Container for hyperlink-behaviour properties, "meta:hyperlink-behaviour".

        The "meta:hyperlink-behaviour" element specifies the default behavior
        for hyperlinks in a document.

        Arguments:

            target_frame_name -- str

            show -- str
        """
        super().__init__(**kwargs)

        if self._do_init:
            self.target_frame_name = target_frame_name
            self.show = show

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} tag={self.tag} "
            f"target={self.target_frame_name} show={self.show}>"
        )

    def __str__(self) -> str:
        return f"({self.target_frame_name})"

    def as_dict(self) -> dict[str, Any]:
        """Return the MetaHyperlinkBehaviour attributes as a Python dict."""
        return {
            "office:target-frame-name": self.target_frame_name,
            "xlink:show": self.show,
        }


MetaHyperlinkBehaviour._define_attribut_property()

register_element_class(MetaHyperlinkBehaviour)
