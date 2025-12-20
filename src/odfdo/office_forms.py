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
        """Retrieve the `office:forms` container within the element.

        Returns:
            OfficeForms | None: The `OfficeForms` instance if found, otherwise `None`.
        """
        return cast(
            Union[None, OfficeForms], self.get_element("descendant::office:forms")
        )

    @property
    def office_forms(self) -> OfficeForms | None:
        """Get the `office:forms` container within the element.

        Returns:
            OfficeForms | None: The `OfficeForms` instance if found, otherwise `None`.
        """
        return self.get_office_forms()


class OfficeForms(FormMixin):
    """Container for "form:form" or "xforms:model" elements, "office:forms"."""

    _tag = "office:forms"

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialize the OfficeForms container.

        This element acts as a container for form definitions (`form:form`
        or `xforms:model`). It is usable within elements like `draw:page`,
        `office:text`, `presentation:notes`, `style:master-page`, and `table:table`.

        Args:
            **kwargs: Additional keyword arguments for the parent `FormMixin` class.
        """
        super().__init__(**kwargs)

    @property
    def apply_design_mode(self) -> bool:
        """Get the `form:apply-design-mode` attribute.

        Returns:
            bool: True if design mode is applied, False otherwise. Defaults to True.
        """
        return self._get_attribute_bool_default("form:apply-design-mode", True)

    @apply_design_mode.setter
    def apply_design_mode(self, apply_design_mode: bool) -> None:
        """Set the `form:apply-design-mode` attribute.

        Args:
            apply_design_mode: Whether to apply design mode.
        """
        self._set_attribute_bool_default(
            "form:apply-design-mode", apply_design_mode, True
        )

    @property
    def automatic_focus(self) -> bool:
        """Get the `form:automatic-focus` attribute.

        Returns:
            True if automatic focus is enabled, False otherwise. Defaults to False.
        """
        return self._get_attribute_bool_default("form:automatic-focus", False)

    @automatic_focus.setter
    def automatic_focus(self, automatic_focus: bool) -> None:
        """Set the `form:automatic-focus` attribute.

        Args:
            automatic_focus: Whether to enable automatic focus.
        """
        self._set_attribute_bool_default("form:automatic-focus", automatic_focus, False)


register_element_class(OfficeForms)
