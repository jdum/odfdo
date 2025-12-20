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
"""MetaAutoReload class for "meta:auto-reload" tag."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from .datatype import Duration
from .element import Element, PropDef, PropDefBool, register_element_class


class MetaAutoReload(Element):
    """Container for auto-reload properties, "meta:auto-reload"."""

    _tag = "meta:auto-reload"
    _properties: tuple[PropDef | PropDefBool, ...] = (
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
        """Initialize a MetaAutoReload element.

        The `meta:auto-reload` element specifies whether a document is
        reloaded or replaced by another document after a specified period
        of time has elapsed.

        Args:
            delay: The time delay after which the document
                should auto-reload.
            href: The URL or path to the document to reload or replace with.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)

        self.actuate = "onLoad"
        self.show = "replace"
        self.type = "simple"
        if self._do_init:
            self._set_delay(delay)
            self.href = href

    def __repr__(self) -> str:
        if self.delay:
            delay = str(Duration.decode(self.delay))
        else:
            delay = ""
        return (
            f"<{self.__class__.__name__} tag={self.tag} href={self.href} delay={delay}>"
        )

    def __str__(self) -> str:
        return f"({self.href})"

    def _set_delay(self, delay: timedelta | None) -> None:
        """Set the `meta:delay` attribute from a `timedelta` object.

        Converts the `timedelta` to an ODF duration string. If `delay` is
        None, it defaults to `timedelta(0)`.

        Args:
            delay: The delay duration.
        """
        if delay is None:
            delay = timedelta(0)
        self.delay = Duration.encode(delay)

    def as_dict(self) -> dict[str, Any]:
        """Return the attributes of the auto-reload element as a Python dictionary.

        Returns:
            dict[str, Any]: A dictionary containing the meta auto-reload
                attributes, with keys like "meta:delay", "xlink:href", etc.
        """
        result: dict[str, Any] = {}
        if self.delay:
            result["meta:delay"] = Duration.decode(self.delay)
        else:
            result["meta:delay"] = timedelta(0)
        result.update(
            {
                "xlink:actuate": self.actuate or "onLoad",
                "xlink:href": self.href or "",
                "xlink:show": self.show or "replace",
                "xlink:type": self.type or "simple",
            }
        )
        return result

    def from_dict(self, data: dict[str, Any]) -> None:
        """Set the attributes of the auto-reload element from a Python dictionary.

        Args:
            data: A dictionary containing the meta auto-reload
                attributes (e.g., "meta:delay", "xlink:href").
        """
        self._set_delay(data.get("meta:delay"))
        self.actuate = data.get("xlink:actuate", "onLoad")
        self.href = data.get("xlink:href", "")
        self.show = data.get("xlink:show", "replace")
        self.type = data.get("xlink:type", "simple")


MetaAutoReload._define_attribut_property()

register_element_class(MetaAutoReload)
