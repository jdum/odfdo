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
"""StyleBase, base class of all ODF style classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .element import Element

if TYPE_CHECKING:
    from .style import Style


class StyleBase(Element):
    """Base class of all ODF style classes (internal)."""

    _tag: str = "style:_pseudo_style_base_"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family}>"

    def __str__(self) -> str:
        return repr(self)

    @property
    def family(self) -> str | None:
        return None

    @family.setter
    def family(self, _family: str | None) -> None:
        pass

    def get_properties(self, area: str | None = None) -> dict[str, str | dict] | None:
        """Get the mapping of all properties of this style."""
        return None

    def set_properties(
        self,
        properties: dict[str, str | dict] | None = None,
        style: Style | None = None,
        area: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the properties of the "area" type of this style."""
        pass

    def get_list_style_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced
        values.
        """
        return {}

    def get_text_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced
        values.
        """
        return {}
