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
"""Config elements for the "settings.xml" part.

This module defines classes representing configuration elements found within
the `settings.xml` file of an ODF document, specifically those related to
`config:config-item-set`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .element import Element, PropDef, PropDefBool, register_element_class

if TYPE_CHECKING:
    pass


class ConfigItemSet(Element):
    """Represents a container element for application setting elements,
    "config:config-item-set" tag.

    This element can contain other configuration items, item maps, or item
    sets, forming a hierarchical structure for document settings.

    Attributes:
        name (str): The name of the configuration item set.
    """

    _tag: str = "config:config-item-set"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "text:name"),)

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConfigItemSet element.

        This element acts as a container for various application setting
        elements, including `config:config-item`,
        `config:config-item-map-indexed`, `config:config-item-map-named`,
        and nested `config:config-item-set`.

        Args:
            name: The name of the configuration item set.
            **kwargs: Arbitrary keyword arguments passed to the base `Element`
                class.
        """
        # fixme : use offset
        # TODO allow paragraph and text styles
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"


ConfigItemSet._define_attribut_property()

register_element_class(ConfigItemSet)
