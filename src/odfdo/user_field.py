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

This module provides classes for managing user field declarations and their
instances within the document content, such as 'text:user-field-decls',
'text:user-field-decl', 'text:user-field-get', and 'text:user-defined'.
"""

from __future__ import annotations

from typing import Any

from .document import Document
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
            name (str, optional): The name of the user field to get.
            value (Any, optional): An initial value to display.
            value_type (str, optional): The ODF value type.
            text (str, optional): The textual representation to display. If
                not provided, it's generated from `value`.
            style (str, optional): The data style name for formatting.
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
            name (str): The name of the user-defined field.
            value (Any, optional): The value of the field.
            value_type (str, optional): The ODF value type (e.g., 'string').
            text (str, optional): The textual representation of the value.
            style (str, optional): The data style name for formatting.
            from_document (Document, optional): A document from which to load
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

register_element_class(UserFieldDecls)
register_element_class(UserFieldDecl)
register_element_class(UserFieldGet)
register_element_class(UserFieldInput)
register_element_class(UserDefined)
