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
'text:variable-decl' and variable declaration container
'text:variable-decls'."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


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
            name (str, optional): The name of the variable.
            value_type (str, optional): The ODF value type.
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
