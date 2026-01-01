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
"""Representation of the "settings.xml" part of the ODF document.

This part stores document-wide settings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, cast

from .body import OfficeSettings
from .config_elements import ConfigItemSet
from .element import Element
from .xmlpart import XmlPart

if TYPE_CHECKING:
    pass


class Settings(XmlPart):
    """Representation of the "settings.xml" part of the ODF document.

    This part stores document-wide settings.
    """

    def _get_body(self) -> OfficeSettings:
        body = cast(Union[None, OfficeSettings], self.get_element("//office:settings"))
        if not isinstance(body, OfficeSettings):
            raise TypeError("No OfficeSettings found")
        return body

    @property
    def odf_office_version(self) -> str:
        """Get the "office:version" value of the settings part.

        This value indicates the ODF version of the document settings.

        Returns:
            str: The "office:version" value, or an empty string if not found.
        """
        odsettings = cast(
            Union[None, Element], self.get_element("//office:document-settings")
        )
        # "office:version" sould be always present
        if odsettings:
            return odsettings.get_attribute_string("office:version") or ""
        return ""  # pragma: nocover

    @property
    def config_item_sets(self) -> list[ConfigItemSet]:
        """Get a list of first-level ConfigItemSet elements within the
        settings.

        These represent top-level configuration item sets in the document's
        settings.

        Returns:
        list[ConfigItemSet]: A list of `ConfigItemSet` objects.
        """
        return cast(
            list[ConfigItemSet], self.body.get_elements("config:config-item-set")
        )

    def as_dict(self) -> dict[str, str | int | bool | dict[str, Any] | list[Any]]:
        """Serialize the settings content into a dictionary.

        This method delegates the serialization to the underlying
        `OfficeSettings` body, returning a dictionary representation of
        the settings.

        Returns:
            dict: A dictionary representing the settings content.
        """
        body: OfficeSettings = cast(OfficeSettings, self.body)
        return body.as_dict()
