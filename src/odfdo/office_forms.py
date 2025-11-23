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
"""OfficeForms class for "office:forms" tag."""

from __future__ import annotations

from typing import Any, Union, cast

from .element import Element, register_element_class
from .form import FormMixin


class OfficeFormsMixin(Element):
    """Mixin class for classes containing the OfficeForms container.

    Used by the following classes: "draw:page", "office:text",
    "presentation:notes", "style:master-page", "table:table".
    """

    def get_office_forms(self) -> OfficeForms | None:
        """Return the OfficeForms if exists.

        Returns: OfficeForms or None if not found
        """
        return cast(
            Union[None, OfficeForms], self.get_element("descendant::office:forms")
        )

    @property
    def office_forms(self) -> OfficeForms | None:
        return self.get_office_forms()


class OfficeForms(FormMixin):
    """Container for "form:form" or "xforms:model" elements, "office:forms"."""

    _tag = "office:forms"

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        """OfficeForms container for the document, "office:forms".

        The "office:forms" element is usable within the following elements:
        "draw:page", "office:text", "presentation:notes", "style:master-page",
        "table:table".
        """
        super().__init__(**kwargs)

    @property
    def apply_design_mode(self) -> bool:
        return self._get_attribute_bool_default("form:apply-design-mode", True)

    @apply_design_mode.setter
    def apply_design_mode(self, apply_design_mode: bool) -> None:
        self._set_attribute_bool_default(
            "form:apply-design-mode", apply_design_mode, True
        )

    @property
    def automatic_focus(self) -> bool:
        return self._get_attribute_bool_default("form:automatic-focus", False)

    @automatic_focus.setter
    def automatic_focus(self, automatic_focus: bool) -> None:
        self._set_attribute_bool_default("form:automatic-focus", automatic_focus, False)


register_element_class(OfficeForms)
