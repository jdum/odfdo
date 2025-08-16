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
"""MetaTemplate class for "meta:template" tag."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .datatype import DateTime
from .element import Element, PropDef, register_element_class


class MetaTemplate(Element):
    """Container for the meta template properties, "meta:template"."""

    _tag = "meta:template"
    _properties: tuple[PropDef, ...] = (
        PropDef("date", "meta:date"),
        PropDef("actuate", "xlink:actuate"),
        PropDef("href", "xlink:href"),
        PropDef("title", "xlink:title"),
        PropDef("type", "xlink:type"),
    )

    def __init__(
        self,
        date: datetime | None = None,
        href: str = "",
        title: str = "",
        **kwargs: Any,
    ) -> None:
        """Container for the meta template properties, "meta:template".

        The <meta:template> element specifies a URI for the document template
        that was used to create a document. The URI is specified as an
        Xlink.

        Arguments:

            date -- datetime or None

            href -- str

            title -- str
        """
        super().__init__(**kwargs)

        self.actuate = "onRequest"
        self.type = "simple"
        if self._do_init:
            self._set_date(date)
            self.href = href
            self.title = title

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} href={self.href}>"

    def __str__(self) -> str:
        if self.title:
            return f"[{self.title}]({self.href})"
        return f"({self.href})"

    def _set_date(self, date: datetime | None) -> None:
        if date is None:
            date = datetime.now()
        self.date = DateTime.encode(date)

    def as_dict(self) -> dict[str, Any]:
        """Return the MetaTemplate attributes as a Python dict."""
        result: dict[str, Any] = {}
        if self.date:
            result["meta:date"] = DateTime.decode(self.date)
        result.update(
            {
                "xlink:actuate": self.actuate or "",
                "xlink:href": self.href or "",
                "xlink:title": self.title or "",
                "xlink:type": self.type or "",
            }
        )
        return result

    def from_dict(self, data: dict[str, Any]) -> None:
        """Set all the MetaTemplate attributes from a Python dict."""
        self._set_date(data.get("meta:date"))
        self.actuate = data.get("xlink:actuate", "onRequest")
        self.href = data.get("xlink:href", "")
        self.title = data.get("xlink:title", "")
        self.type = data.get("xlink:type", "simple")


MetaTemplate._define_attribut_property()

register_element_class(MetaTemplate)
