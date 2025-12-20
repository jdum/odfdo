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
"""Classes for ODF document user fields declarations.

This module provides classes for managing user field declarations and their
containers within the document content, tags "text:user-field-decl",
"text:user-field-decls".
.
"""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .element_typed import ElementTyped


class UserFieldDecls(Element):
    """A container for user field declarations, "text:user-field-decls".

    This element groups all the 'text:user-field-decl' elements in the
    document's meta information.
    """

    _tag = "text:user-field-decls"


class UserFieldDecl(ElementTyped):
    """A declaration of a user field, "text:user-field-decl".

    This element, typically found within 'text:user-field-decls', defines a
    user-defined field, its name, type, and current value.

    Attributes:
        name (str): The unique name of the user field.
    """

    _tag = "text:user-field-decl"
    _properties = (PropDef("name", "text:name"),)

    def __init__(
        self,
        name: str | None = None,
        value: Any = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the UserFieldDecl element.

        Args:
            name (str, optional): The name of the user field.
            value (Any, optional): The initial value of the field.
            value_type (str, optional): The ODF value type (e.g., 'string',
                'float'). If not provided, it is inferred from the `value`.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            self.set_value_and_type(value=value, value_type=value_type)

    def set_value(self, value: Any) -> None:
        """Sets the value of the user field declaration.

        This method updates the value and value type of the declaration,
        preserving its name.

        Args:
            value (Any): The new value for the field.
        """
        name = self.get_attribute("text:name")
        self.clear()
        self.set_value_and_type(value=value)
        self.set_attribute("text:name", name)


UserFieldDecl._define_attribut_property()


register_element_class(UserFieldDecls)
register_element_class(UserFieldDecl)
