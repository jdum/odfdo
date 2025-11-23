# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Forms class for "form:form" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


class Form(Element):
    """Specification a user-interface form and defines the contents and
    properties of the form, "form:form".

    The "form:form" element is usable within the following elements:
    "form:form" and "office:forms".

    (The main objective of the current minimal implementation is to parse
    the existing form in a document.)
    """

    _tag = "form:form"
    _properties = (
        PropDef("name", "form:name"),
        PropDef("command", "form:command"),
        PropDef("datasource", "form:datasource"),
        PropDef("apply_filter", "form:apply-filter"),
        PropDef("command_type", "form:command-type"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("target_frame", "office:target-frame"),
    )

    def __init__(
        self,
        name: str = "Form",
        command: str | None = None,
        datasource: str | None = None,
        apply_filter: bool | None = None,
        command_type: str | None = None,
        control_implementation: str | None = None,
        target_frame: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a Form, "form:form".

        The "form:form" element is usable within the following elements:
        "form:form" and "office:forms".

        Args:

            name -- str

            command -- str

            datasource -- str

            apply_filter -- bool

            command_type -- str

            control_implementation -- bool

            target_frame -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name is not None:
                self.name = name
            if command is not None:
                self.command = command
            if datasource is not None:
                self.datasource = datasource
            if apply_filter is not None:
                self.apply_filter = apply_filter
            if command_type is not None:
                self.command_type = command_type
            if control_implementation is not None:
                self.control_implementation = control_implementation
            if target_frame is not None:
                self.target_frame = target_frame


Form._define_attribut_property()

register_element_class(Form)
