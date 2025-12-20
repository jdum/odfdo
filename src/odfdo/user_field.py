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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Classes related to user-defined fields in ODF documents.

This module provides classes for managing user field declarations
content within the document, "text:user-defined", text:user-field-get",
"text:user-field-input".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, cast

from .element import Element, PropDef, register_element_class
from .element_typed import ElementTyped

# for compatibility for version <= 3.18.2
from .user_field_declaration import (  # noqa: F401
    UserFieldDecl,
    UserFieldDecls,
)

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    from decimal import Decimal

    from .document import Document


class UserDefinedMixin(Element):
    """Mixin class for classes containing user defined fields.

    Used by the following classes:
        - "text:a"
        - "text:h"
        - "text:meta"
        - "text:meta-field"
        - "text:p"
        - "text:ruby-base"
        - "text:span"

    and "office:text", "office:spreadsheet","office:presentation" for
    compatibility with previous versions.
    """

    def get_user_defined_list(self) -> list[UserDefined]:
        """Returns all user-defined field declarations as a list.

        Returns:
            list[UserDefined]: A list of all UserDefined instances that are descendants of this element.
        """
        return cast(
            list[UserDefined],
            self._filtered_elements(
                "descendant::text:user-defined",
            ),
        )

    @property
    def user_defined_list(self) -> list[UserDefined]:
        """Returns all user-defined field declarations as a list.

        Returns:
            list[UserDefined]: A list of all UserDefined instances that are descendants of this element.
        """
        return self.get_user_defined_list()

    def get_user_defined(self, name: str, position: int = 0) -> UserDefined | None:
        """Returns a single user-defined field declaration that matches the specified criteria.

        Args:
            name: The name of the user-defined field to retrieve.
            position: The 0-based index of the matching user-defined field to return.

        Returns:
            UserDefined | None: A UserDefined instance, or None if no declaration matches the criteria.
        """
        return cast(
            Union[None, UserDefined],
            self._filtered_element(
                "descendant::text:user-defined", position, text_name=name
            ),
        )

    def get_user_defined_value(
        self, name: str, value_type: str | None = None
    ) -> bool | str | int | float | Decimal | datetime | timedelta | None:
        """Returns the value of the specified user-defined field.

        Args:
            name: The name of the user-defined field to retrieve its value.
            value_type: The expected type of the user-defined field's value.
                Can be 'boolean', 'date', 'float', 'string', 'time', or None
                for automatic type detection.

        Returns:
            bool | str | int | float | Decimal | datetime | timedelta | None:
                The value of the user-defined field, cast to the most appropriate
                Python type, or None if the user-defined field is not found.
        """
        user_defined = self.get_user_defined(name)
        if user_defined is None:
            return None
        return user_defined.get_value(value_type)  # type: ignore[return-value]


class UserFieldGet(ElementTyped):
    """A getter for a user field value, "text:user-field-get".

    This element displays the current value of a user-defined field at a
    specific position in the document content.

    Attributes:
        name (str): The name of the user field to display.
        style (str, optional): The data style to apply for formatting the
            displayed value.
    """

    _tag = "text:user-field-get"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("style", "style:data-style-name"),
    )

    def __init__(
        self,
        name: str | None = None,
        value: Any = None,
        value_type: str | None = None,
        text: str | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the UserFieldGet element.

        Args:
            name: The name of the user field to get.
            value: An initial value to display.
            value_type: The ODF value type.
            text: The textual representation to display. If
                not provided, it's generated from `value`.
            style: The data style name for formatting.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            text = self.set_value_and_type(
                value=value, value_type=value_type, text=text
            )
            self.text = text

            if style:
                self.style = style


UserFieldGet._define_attribut_property()


class UserFieldInput(UserFieldGet):
    """An input field for a user-defined field, "text:user-field-input".

    This element allows the user to interactively modify the value of a
    user-defined field within the document.
    """

    _tag = "text:user-field-input"


UserFieldInput._define_attribut_property()


class UserDefined(ElementTyped):
    """A user-defined field instance, "text:user-defined".

    This element is similar to 'text:user-field-get' but is often used in
    contexts like headers or footers. It can be initialized directly with
    a value or can pull its value from a corresponding user-defined metadata
    field in the document's meta section.

    Attributes:
        name (str): The name of the user field.
        style (str, optional): The data style to apply for formatting.
    """

    _tag = "text:user-defined"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("style", "style:data-style-name"),
    )

    def __init__(
        self,
        name: str = "",
        value: Any = None,
        value_type: str | None = None,
        text: str | None = None,
        style: str | None = None,
        from_document: Document | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the UserDefined element.

        If a document is provided via `from_document`, the element will be
        populated with the value of the meta user-defined field of the same
        name from that document.

        Args:
            name: The name of the user-defined field.
            value: The value of the field.
            value_type: The ODF value type (e.g., 'string').
            text: The textual representation of the value.
            style: The data style name for formatting.
            from_document: A document from which to load
                the field's value from the meta section.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if from_document is not None:
                meta_infos = from_document.meta
                content = meta_infos.get_user_defined_metadata_of_name(name)
                if content is not None:
                    value = content.get("value", None)
                    value_type = content.get("value_type", None)
                    text = content.get("text", None)
            text = self.set_value_and_type(
                value=value, value_type=value_type, text=text
            )
            self.text = text


UserDefined._define_attribut_property()

register_element_class(UserFieldGet)
register_element_class(UserFieldInput)
register_element_class(UserDefined)
