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
"""Mixin class for "dc:date"."""

from __future__ import annotations

from datetime import datetime

from .datatype import DateTime
from .element import Element


class DcDateMixin:
    """Date of the document, "dc:date"."""

    def get_modification_date(self) -> datetime | None:
        """Get the last modified date of the document.

        (Also available as "self.date" property.)

        Return: datetime (or None if inexistant)
        """
        element = self.clone.get_element("//dc:date")
        if element is None:
            return None
        dtdate = element.text
        return DateTime.decode(dtdate)

    def set_modification_date(self, date: datetime | None = None) -> None:
        """Set the last modified date of the document.

        If provided datetime is None, use current time.

        (Also available as "self.date" property.)

        Arguments:

            dtdate -- datetime
        """
        element = self.get_element("//dc:date")
        if element is None:
            element = Element.from_tag("dc:date")
            if hasattr(self, "get_meta_body"):
                self.get_meta_body().append(element)
            else:
                self.append(element)
        if date is None:
            date = datetime.now()
        element.text = DateTime.encode(date)

    # alias for ChangeInfo class
    set_dc_date = set_modification_date

    @property
    def date(self) -> datetime | None:
        """Get or set the <dc:date> element.

        If provided datetime is None, use current time.

        The <dc:date> element specifies the date and time when the
        document was last modified (<office:meta>), when an annotation
        was created (<office:annotation>), when a change was made
        (<office:change-info>).
        """
        return self.get_modification_date()

    @date.setter
    def date(self, date: datetime | None = None) -> None:
        self.set_modification_date(date)
