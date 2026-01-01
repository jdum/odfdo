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

from typing import TYPE_CHECKING, Any, cast

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
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "config:name"),)

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

        The "config:config-item-set" element has the following child elements:
        "config:config-item", "config:config-item-map-indexed",
        "config:config-item-map-named" and "config:config-item-set"

        Args:
            name: The name of the configuration item set.
            **kwargs: Arbitrary keyword arguments passed to the base `Element`
                class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_item_sets(self) -> list[ConfigItemSet]:
        """Get the list of ConfigItemSet elements of this level.

        Returns:
            list[ConfigItemSet]: A list of `ConfigItemSet` objects.
        """
        return cast(list[ConfigItemSet], self.get_elements("config:config-item-set"))

    @property
    def config_item_maps_indexed(self) -> list[ConfigItemMapIndexed]:
        """Return the list of ConfigItemMapIndexed of this level.

        Returns:
            list[ConfigItemMapIndexed]: A list of `ConfigItemMapIndexed` objects."""
        return cast(
            list[ConfigItemMapIndexed],
            self.get_elements("config:config-item-map-indexed"),
        )


ConfigItemSet._define_attribut_property()


class ConfigItemMapIndexed(Element):
    """Represents a container for ordered sequences of application settings,
    corresponding to the "config:config-item-map-indexed" tag.

    This element is used to store a collection of configuration items that are
    ordered and can be accessed by index.

    Attributes:
        name (str): The name of the indexed configuration item map.
    """

    _tag: str = "config:config-item-map-indexed"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "config:name"),)

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConfigItemMapIndexed element.

        This container holds ordered sequences of application settings.

        The "config:config-item-map-indexed" element has the following child
        element: "config:config-item-map-entry".

        Args:
            name: The name of the indexed configuration item map.
            **kwargs: Arbitrary keyword arguments passed to the base `Element`
                class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_item_maps_entries(self) -> list[ConfigItemMapEntry]:
        """Return list of ConfigItemMapEntry."""
        return cast(
            list[ConfigItemMapEntry], self.get_elements("config:config-item-map-entry")
        )


ConfigItemMapIndexed._define_attribut_property()


class ConfigItemMapEntry(Element):
    """Represents a single setting entry in a sequence of settings,
    corresponding to the "config:config-item-map-entry" tag.

    The setting itself is defined by the child element of "config:config-item-map-entry",
    and may be a single value, a set of settings, or a sequence of settings.

    The "config:config-item-map-entry" element has the following child elements:
    "config:config-item", "config:config-item-map-indexed", "config:config-item-map-named",
    and "config:config-item-set.

    Attributes:
        name (str): The name of the entry.
    """

    _tag: str = "config:config-item-map-entry"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "config:name"),)

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConfigItemMapEntry element.

        This represents an entry within an ordered configuration map.

        Args:
            name: The name of the entry.
            **kwargs: Arbitrary keyword arguments passed to the base `Element`
                class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_item_maps_indexed(self) -> list[ConfigItemMapIndexed]:
        """Return list of ConfigItemMapIndexed."""
        return cast(
            list[ConfigItemMapIndexed],
            self.get_elements("config:config-item-map-indexed"),
        )


ConfigItemMapEntry._define_attribut_property()


class ConfigItemMapNamed(Element):
    """Represents a container for a sequence of application setting elements,
    where each sequence is identified by the value of its `config:name`
    attribute. This corresponds to the "config:config-item-map-named" tag.

    This element is used to store a collection of configuration items that
    can be accessed by a descriptive name rather than an index.

    The "config:config-item-map-named" element has the following child
    element: "config:config-item-map-entry".

    Attributes:
        name (str): The name of the named configuration item map.
    """

    _tag: str = "config:config-item-map-named"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("name", "config:name"),)

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConfigItemMapNamed element.

        This container holds named sequences of application setting elements.

        Args:
            name: The name of the named configuration item map.
            **kwargs: Arbitrary keyword arguments passed to the base `Element`
                class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_item_maps_entries(self) -> list[ConfigItemMapEntry]:
        """Return list of ConfigItemMapEntry."""
        return cast(
            list[ConfigItemMapEntry], self.get_elements("config:config-item-map-entry")
        )


ConfigItemMapNamed._define_attribut_property()

register_element_class(ConfigItemMapEntry)
register_element_class(ConfigItemMapIndexed)
register_element_class(ConfigItemMapNamed)
register_element_class(ConfigItemSet)
