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
"""Classes of Form controls like "form:text", "form:textarea", "form:password" ...

(The main objective of the current minimal implementation of forms is to parse
the existing form contents in a document.)"""

from __future__ import annotations

from typing import Any, cast

from .element import Element, PropDef, register_element_class


class FormHidden(Element):
    """A control that does not have a visual representation, "form:hidden"."""

    _tag = "form:hidden"
    _properties = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = "Form",
        value: str | None = None,
        control_implementation: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormHidden, "form:hidden".

        The "form:hidden" element is usable within the following element:
        "form:form".

         Args:

             name -- str

             value -- str

             control_implementation -- str

             xml_id -- str

             xforms_bind -- str

             form_id -- str
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name is not None:
                self.name = name
            if value is not None:
                self.value = value
            if control_implementation is not None:
                self.control_implementation = control_implementation
            if xml_id is not None:
                self.xml_id = xml_id
            if xforms_bind is not None:
                self.xforms_bind = xforms_bind
            if form_id is None:
                self.form_id = self.xml_id
            else:
                self.form_id = form_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} xml_id={self.xml_id}>"


FormHidden._define_attribut_property()

register_element_class(FormHidden)
