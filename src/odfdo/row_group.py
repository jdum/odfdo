# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""RowGroup class for "table:table-row-group" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, register_element_class
from .row import Row


class RowGroup(Element):
    """ODF row group "table:table-row-group" with common properties.

    Partial implementation.

    The <table:table-row-group> element groups adjacent table rows.
    Every row group can contain header rows, and nested row groups.
    A row group can be visible or hidden."""

    # TODO
    _tag = "table:table-row-group"

    def __init__(
        self,
        height: int | None = None,
        width: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a group of rows, optionnaly filled with "height" number of
        rows, of "width" cells each.

        Row group bear style information applied to a series of rows.

        Arguments:

            height -- int

            width -- int
        """
        super().__init__(**kwargs)
        if self._do_init and height is not None:
            for _i in range(height):
                row = Row(width=width)
                self.append(row)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


register_element_class(RowGroup)
