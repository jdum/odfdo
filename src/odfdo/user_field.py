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
"""User fields classes."""

from __future__ import annotations

from typing import Any

from .document import Document
from .element import Element, PropDef, register_element_class
from .element_typed import ElementTyped


class UserFieldDecls(Element):
    """Container of user fields declarations, "text:user-field-decls"."""

    _tag = "text:user-field-decls"


class UserFieldDecl(ElementTyped):
    """Declaration of a user field, "text:user-field-decl"."""

    _tag = "text:user-field-decl"
    _properties = (PropDef("name", "text:name"),)

    def __init__(
        self,
        name: str | None = None,
        value: Any = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a user field "text:user-field-decl"."""
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            self.set_value_and_type(value=value, value_type=value_type)

    def set_value(self, value: Any) -> None:
        name = self.get_attribute("text:name")
        self.clear()
        self.set_value_and_type(value=value)
        self.set_attribute("text:name", name)


UserFieldDecl._define_attribut_property()


class UserFieldGet(ElementTyped):
    """Representation of user field getter, "text:user-field-get"."""

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
        """Create a user field getter "text:user-field-get"."""
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            text = self.set_value_and_type(
                value=value, value_type=value_type, text=text
            )
            self.text = text  # type: ignore

            if style:
                self.style = style


UserFieldGet._define_attribut_property()


class UserFieldInput(UserFieldGet):
    """Representation of user field input, "text:user-field-input"."""

    _tag = "text:user-field-input"


UserFieldInput._define_attribut_property()


class UserDefined(ElementTyped):
    """A user defined field, "text:user-defined"."""

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
        """Create a user defined field "text:user-defined".

        If the current document is provided, try to extract
        the content of the meta user defined field of same name.

        Arguments:

            name -- str, name of the user defined field

            value -- python typed value, value of the field

            value_type -- str, office:value-type known type

            text -- str

            style -- str

            from_document -- ODF document
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
            self.text = text  # type: ignore


UserDefined._define_attribut_property()

register_element_class(UserFieldDecls)
register_element_class(UserFieldDecl)
register_element_class(UserFieldGet)
register_element_class(UserFieldInput)
register_element_class(UserDefined)
