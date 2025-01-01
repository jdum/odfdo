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
"""MetaAutoReload class for "meta:auto-reload".
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from .datatype import Duration
from .element import Element, PropDef, register_element_class


class MetaAutoReload(Element):
    _tag = "meta:auto-reload"
    _properties: tuple[PropDef, ...] = (
        PropDef("delay", "meta:delay"),
        PropDef("actuate", "xlink:actuate"),
        PropDef("href", "xlink:href"),
        PropDef("show", "xlink:show"),
        PropDef("type", "xlink:type"),
    )

    def __init__(
        self,
        delay: timedelta | None = None,
        href: str = "",
        **kwargs: Any,
    ) -> None:
        """
        The <meta:auto-reload> element specifies whether a document is
        reloaded or replaced by another document after a specified period
        of time has elapsed.

        Arguments:

            delay -- timedelta

            href -- str
        """
        super().__init__(**kwargs)

        self.actuate = "onLoad"
        self.show = "replace"
        self.type = "simple"
        if self._do_init:
            if not isinstance(delay, timedelta):
                raise TypeError("delay must be a timedelta")
            self.delay = Duration.encode(delay)
            self.href = href

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} tag={self.tag} "
            f"href={self.href} delay={Duration.decode(self.delay)}>"
        )

    def __str__(self) -> str:
        return f"({self.href})"

    def as_dict(self) -> dict[str, Any]:
        """Return the MetaAutoReload attributes as a Python dict."""
        return {
            "meta:delay": self.delay,
            "xlink:actuate": self.actuate,
            "xlink:href": self.href,
            "xlink:show": self.show,
            "xlink:type": self.type,
        }


MetaAutoReload._define_attribut_property()
register_element_class(MetaAutoReload)
