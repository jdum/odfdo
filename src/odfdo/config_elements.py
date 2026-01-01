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

from typing import TYPE_CHECKING, Any, ClassVar, cast

from .datatype import Boolean
from .element import Element, PropDef, PropDefBool, register_element_class

if TYPE_CHECKING:
    pass


def _as_dict(
    element: ConfigItemMapEntry
    | ConfigItemMapIndexed
    | ConfigItemMapNamed
    | ConfigItemSet,
) -> dict[str, str | int | bool | dict[str, Any]]:
    conf: dict[str, str | list[Any]] = {"class": element._tag}
    if element.name:
        conf["config:name"] = element.name
    # all children are known to be classes with as_dict()
    children = [child.as_dict() for child in element.children]  # type: ignore[attr-defined]
    if children:
        conf["children"] = children
    return conf


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

    @property
    def config_item_maps_named(self) -> list[ConfigItemMapNamed]:
        """Return list of ConfigItemMapNamed."""
        return cast(
            list[ConfigItemMapNamed], self.get_elements("config:config-item-map-named")
        )

    @property
    def config_items(self) -> list[ConfigItem]:
        """Return list of ConfigItem."""
        return cast(list[ConfigItem], self.get_elements("config:config-item"))

    def as_dict(self) -> dict[str, str | int | bool | dict]:
        return _as_dict(self)


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

    def as_dict(self) -> dict[str, str | int | bool | dict]:
        return _as_dict(self)


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
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_item_sets(self) -> list[ConfigItemSet]:
        """Return list of first level ConfigItemSet."""
        return cast(list[ConfigItemSet], self.get_elements("config:config-item-set"))

    @property
    def config_item_maps_indexed(self) -> list[ConfigItemMapIndexed]:
        """Return list of ConfigItemMapIndexed."""
        return cast(
            list[ConfigItemMapIndexed],
            self.get_elements("config:config-item-map-indexed"),
        )

    @property
    def config_item_maps_named(self) -> list[ConfigItemMapNamed]:
        """Return list of ConfigItemMapNamed."""
        return cast(
            list[ConfigItemMapNamed], self.get_elements("config:config-item-map-named")
        )

    @property
    def config_items(self) -> list[ConfigItem]:
        """Return list of ConfigItem."""
        return cast(list[ConfigItem], self.get_elements("config:config-item"))

    def as_dict(self) -> dict[str, str | int | bool | dict]:
        return _as_dict(self)


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

    def as_dict(self) -> dict[str, str | int | bool | dict]:
        return _as_dict(self)


ConfigItemMapNamed._define_attribut_property()


class ConfigItem(Element):
    """Represents an element containing the value of an application setting,
    identified by its `config:name` attribute. This corresponds to the
    "config:config-item" tag.

    This element holds a single configuration value and does not have any
    child elements.

    Attributes:
        name (str): The name of the configuration item.
        config_type (str): The data type of the configuration item's value.
    """

    _tag: str = "config:config-item"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "config:name"),
        PropDef("config_type", "config:type"),
    )
    _properties = (PropDef("name", "config:name"),)
    TYPES: ClassVar = {
        "boolean",
        "short",
        "int",
        "long",
        "double",
        "string",
        "datetime",
        "base64Binary",
    }

    def __init__(
        self,
        name: str | None = None,
        config_type: str | None = None,
        value: str | int | bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ConfigItem element.

        This element contains the value of an application setting.

        Args:
            name: The name of the configuration item.
            config_type: The data type of the configuration item's value,
                one of "boolean", "short", "int", "long", "double", "string",
                "datetime", or "base64Binary".
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.config_type = config_type
            self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag} name={self.name}>"

    @property
    def config_type(self) -> str:
        config_type = self.get_attribute_string("config:type")
        if config_type not in self.TYPES:
            return "string"
        return config_type

    @config_type.setter
    def config_type(self, config_type: str | None) -> None:
        if config_type not in self.TYPES:
            config_type = "string"
        self._set_attribute_str("config:type", config_type)

    @property
    def value(self) -> str | int | bool:
        content: str = self.text
        config_type = self.config_type
        if config_type == "boolean":
            return Boolean.decode(content)
        elif config_type in {"short", "int", "long", "double"}:
            return int(content)
        return content or ""

    @value.setter
    def value(self, value: str | int | bool | None) -> None:
        config_type = self.config_type
        if config_type == "boolean":
            self.text = Boolean.encode(value)
        elif config_type in {"short", "int", "long", "double"}:
            self.text = str(int(value))  # type: ignore[arg-type]
        else:
            self.text = str(value or "")

    def as_dict(self) -> dict[str, str | int | bool]:
        return {
            "class": self._tag,
            "config:name": self.name,
            "config:type": self.config_type,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | int | bool]) -> ConfigItem:
        return cls(
            name=data["config:name"],
            config_type=data.get("config:type"),
            value=data.get("value"),
        )


ConfigItem._define_attribut_property()

register_element_class(ConfigItem)
register_element_class(ConfigItemMapEntry)
register_element_class(ConfigItemMapIndexed)
register_element_class(ConfigItemMapNamed)
register_element_class(ConfigItemSet)
