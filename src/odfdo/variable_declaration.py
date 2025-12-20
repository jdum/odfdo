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
"""Classes for ODF document variables declarations.

This module provides classes for managing variable declaration
"text:variable-decl" and variable declaration container
"text:variable-decls"."""

from __future__ import annotations

from typing import Any, Union, cast

from .element import FIRST_CHILD, Element, PropDef, register_element_class


class VarDeclMixin(Element):
    """Mixin class for elements that can contain variable declarations.

    This mixin provides methods to access and manipulate "text:variable-decls"
    and "text:variable-decl".

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
    """

    def get_variable_decls(self) -> VarDecls:
        """Returns the container for variable declarations.

        If the container is not found, it is created within the document body.

        Returns:
            VarDecls: The VarDecls instance (container for variable declarations).

        Raises:
            ValueError: If the document body is empty and a new container cannot be inserted.
        """
        variable_decls = self.get_element("//text:variable-decls")
        if variable_decls is None:
            body = self.document_body
            if not body:
                raise ValueError("Empty document.body")
            body.insert(Element.from_tag("text:variable-decls"), FIRST_CHILD)
            variable_decls = body.get_element("//text:variable-decls")

        return cast(VarDecls, variable_decls)

    def get_variable_decl_list(self) -> list[VarDecls]:
        """Returns all variable declarations as a list.

        Returns:
            list[VarDecls]: A list of all VarDecls instances that are descendants of this element.
        """
        return cast(
            list[VarDecls], self._filtered_elements("descendant::text:variable-decl")
        )

    def get_variable_decl(self, name: str, position: int = 0) -> VarDecls | None:
        """Returns a single variable declaration that matches the specified criteria.

        Args:
            name: The name of the variable declaration to retrieve.
            position: The 0-based index of the matching variable declaration to return.

        Returns:
            VarDecls | None: A VarDecls instance, or None if no declaration matches the criteria.
        """
        return cast(
            Union[None, VarDecls],
            self._filtered_element(
                "descendant::text:variable-decl", position, text_name=name
            ),
        )


class VarDecls(Element):
    """A container for variable declarations, "text:variable-decls".

    This element groups all the 'text:variable-decl' elements in the
    document.
    """

    _tag = "text:variable-decls"


class VarDecl(Element):
    """A variable declaration, "text:variable-decl".

    This element defines a variable by its name and value type.

    Attributes:
        name (str): The unique name of the variable.
        value_type (str): The ODF value type (e.g., 'string', 'float').
    """

    _tag = "text:variable-decl"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("value_type", "office:value-type"),
    )

    def __init__(
        self,
        name: str | None = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarDecl element.

        Args:
            name: The name of the variable.
            value_type: The ODF value type.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if value_type:
                self.value_type = value_type


VarDecl._define_attribut_property()


register_element_class(VarDecls)
register_element_class(VarDecl)
