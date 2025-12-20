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
containers within the document content, tags "text:user-field-decls",
"text:user-field-decl".
.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, cast

from .element import FIRST_CHILD, Element, PropDef, register_element_class
from .element_typed import ElementTyped

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    from decimal import Decimal


class UserFieldDeclMixin(Element):
    """Mixin class for elements that can contain user field declarations.

    This mixin provides methods to access "text:user-field-decl".

    Used by the following classes:
        - "office:chart"
        - "office:drawing"
        - "office:presentation"
        - "office:spreadsheet"
        - "office:text"
        - "style:footer"
        - "style:footer-first"
        - "style:footer-left"
        - "style:header"
        - "style:header-first"
        - "style:header-left"
        - "text:user-field-decls"
    """

    def get_user_field_decl_list(self) -> list[UserFieldDecl]:
        """Returns all user field declarations as a list.

        Returns:
            list[UserFieldDecl]: A list of all UserFieldDecl instances that
            are descendants of this element.
        """
        return cast(
            list[UserFieldDecl],
            self._filtered_elements(
                "descendant::text:user-field-decl",
            ),
        )

    def get_user_field_decl(self, name: str, position: int = 0) -> UserFieldDecl | None:
        """Returns a single user field declaration that matches the specified
        criteria.

        Args:
            name: The name of the user field declaration to retrieve.
            position: The 0-based index of the matching user field
            declaration to return.

        Returns:
            UserFieldDecl | None: A UserFieldDecl instance, or None if no
            declaration matches the criteria.
        """
        return cast(
            Union[None, UserFieldDecl],
            self._filtered_element(
                "descendant::text:user-field-decl", position, text_name=name
            ),
        )

    def get_user_field_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Returns the value of the specified user field.

        Args:
            name: The name of the user field to retrieve its value.
            value_type: The expected type of the user field's value.
                Can be 'boolean', 'currency', 'date', 'float',
                'percentage', 'string', 'time', or None for automatic
                type detection.

        Returns:
            bool | str | int | float | Decimal | datetime | timedelta | None:
                The value of the user field, cast to the most appropriate
                Python type, or None if the user field is not found.
        """
        user_field_decl = self.get_user_field_decl(name)
        if user_field_decl is None:
            return None
        value = user_field_decl.get_value(value_type)
        return value  # type: ignore


class UserFieldDeclContMixin(UserFieldDeclMixin):
    """Mixin class for elements that can contain user field declarations.

    This mixin provides methods to access and manipulate
    "text:user-field-decls" and "text:user-field-decl".

    Used by the following classes:
        UserFieldDecls
        - "office:chart"
        - "office:drawing"
        - "office:presentation"
        - "office:spreadsheet"
        - "office:text"
        - "style:footer"
        - "style:footer-first"
        - "style:footer-left"
        - "style:header"
        - "style:header-first"
        - "style:header-left"
    """

    def get_user_field_decls(self) -> UserFieldDecls:
        """Returns the container for user field declarations.

        If the container is not found, it is created within the document body.

        Returns:
            UserFieldDecls: The UserFieldDecls instance (container for
                user field declarations).

        Raises:
            ValueError: If the document body is empty and a new container
                cannot be inserted.
        """
        user_field_decls = self.get_element("//text:user-field-decls")
        if user_field_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:user-field-decls"), FIRST_CHILD)
            user_field_decls = body.get_element("//text:user-field-decls")

        return cast(UserFieldDecls, user_field_decls)


class UserFieldDecls(UserFieldDeclMixin):
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
            name: The name of the user field.
            value: The initial value of the field.
            value_type: The ODF value type (e.g., 'string',
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
            value: The new value for the field.
        """
        name = self.get_attribute("text:name")
        self.clear()
        self.set_value_and_type(value=value)
        self.set_attribute("text:name", name)


UserFieldDecl._define_attribut_property()


register_element_class(UserFieldDecls)
register_element_class(UserFieldDecl)
