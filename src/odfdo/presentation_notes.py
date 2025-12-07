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
"""Note class for "presentation:notes" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, register_element_class
from .office_forms import OfficeFormsMixin


class PresentationNotes(OfficeFormsMixin, Element):
    """The "presentation:notes" element defines a notes page.

    (Minimal implementation).

    A notes page contains a preview of a drawing page and additional graphic
    shapes.

    The "presentation:notes" element is usable within the following elements:
    "draw:page" and "style:master-page".
    """

    _tag = "presentation:notes"

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        """Initialize a PresentationNotes element.

        The `presentation:notes` element defines a notes page, typically
        containing a preview of a drawing page and additional graphic shapes.

        Args:
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)


register_element_class(PresentationNotes)
