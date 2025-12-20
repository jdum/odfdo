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
"""Classes for ODF document variables and fields.

This module provides classes for various types of document fields that can
be automatically updated, such as dates, times, page numbers, and document
metadata (e.g., author, title). It also includes classes for declaring and
managing custom variables ('text:variable-set', 'text:variable-get').
"""

from __future__ import annotations

from datetime import datetime, timedelta
from datetime import time as dt_time
from typing import Any, ClassVar

from .datatype import Date, DateTime, Duration
from .element import Element, PropDef, register_element_class
from .element_typed import ElementTyped
from .user_field import (  # noqa: F401
    UserDefined,
    UserFieldGet,
    UserFieldInput,
)

# for compatibility for version <= 3.18.2
from .user_field_declaration import (  # noqa: F401
    UserFieldDecl,
    UserFieldDecls,
)


class VarSet(ElementTyped):
    """A variable setter, "text:variable-set".

    This element sets the value of a declared variable. It can optionally
    display the value at its position in the text.

    Attributes:
        name (str): The name of the variable to set.
        style (str, optional): The data style for formatting the displayed
            value.
        display (str): Controls whether the value is displayed ('none' or
            omitted).
    """

    _tag = "text:variable-set"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("style", "style:data-style-name"),
        PropDef("display", "text:display"),
    )

    def __init__(
        self,
        name: str | None = None,
        value: Any = None,
        value_type: str | None = None,
        display: str | bool = False,
        text: str | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarSet element.

        Args:
            name: The name of the variable to set.
            value: The value to assign to the variable.
            value_type: The ODF value type.
            display: If False or 'none', the value is not
                displayed. Otherwise, it is. Defaults to False.
            text: The textual representation of the value.
            style: The data style name for formatting.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            text = self.set_value_and_type(
                value=value, value_type=value_type, text=text
            )
            if not display:
                self.display = "none"
            else:
                self.text = text

    def set_value(self, value: Any) -> None:
        """Sets the value of the variable.

        This method updates the value and value type, preserving other
        attributes like name, style, and display setting.

        Args:
            value: The new value for the variable.
        """
        name = self.get_attribute("text:name")
        display = self.get_attribute("text:display")
        style = self.get_attribute("style:data-style-name")
        self.clear()
        text = self.set_value_and_type(value=value)
        self.set_attribute("text:name", name)
        self.set_attribute("style:data-style-name", style)
        if display is not None:
            self.set_attribute("text:display", display)
        if isinstance(text, str):
            self.text = text


VarSet._define_attribut_property()


class VarGet(ElementTyped):
    """A variable getter, "text:variable-get".

    This element displays the current value of a variable at its position in
    the document.

    Attributes:
        name (str): The name of the variable to display.
        style (str, optional): The data style for formatting the value.
    """

    _tag = "text:variable-get"
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
        """Initializes the VarGet element.

        Args:
            name: The name of the variable to get.
            value: An initial value to display.
            value_type: The ODF value type.
            text: The textual representation to display.
            style: The data style name for formatting.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            text = self.set_value_and_type(
                value=value, value_type=value_type, text=text
            )
            self.text = text


VarGet._define_attribut_property()


class VarPageNumber(Element):
    """A page number field, "text:page-number".

    Displays the page number, which can be the current, previous, or next
    page number, with an optional adjustment.

    Attributes:
        select_page (str): Which page number to display ('current',
            'previous', 'next').
        page_adjust (str): A numerical value to add to or subtract from the
            page number.
    """

    _tag = "text:page-number"
    _properties = (
        PropDef("select_page", "text:select-page"),
        PropDef("page_adjust", "text:page-adjust"),
    )

    def __init__(
        self,
        select_page: str | None = None,
        page_adjust: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarPageNumber element.

        Args:
            select_page: The page to select: 'current' (the
                default), 'previous', or 'next'.
            page_adjust: A numerical value to add to or
                subtract from the selected page number.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if select_page is None:
                select_page = "current"
            self.select_page = select_page
            if page_adjust is not None:
                self.page_adjust = page_adjust


VarPageNumber._define_attribut_property()


class VarPageCount(Element):
    """A page count field, "text:page-count".

    Displays the total number of pages in the document.
    """

    _tag = "text:page-count"


class VarDate(Element):
    """A date field, "text:date".

    Displays a date, which can be fixed or automatically updated.

    Attributes:
        date (str): The date value in ISO 8601 format.
        fixed (bool): If True, the date is not updated automatically.
        data_style (str): The style for formatting the date.
        date_adjust (str): A duration to add to or subtract from the date.
    """

    _tag = "text:date"
    _properties = (
        PropDef("date", "text:date-value"),
        PropDef("fixed", "text:fixed"),
        PropDef("data_style", "style:data-style-name"),
        PropDef("date_adjust", "text:date-adjust"),
    )

    def __init__(
        self,
        date: datetime | None = None,
        fixed: bool = False,
        data_style: str | None = None,
        text: str | None = None,
        date_adjust: timedelta | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarDate element.

        Args:
            date: The date value. If not provided, the
                field may be updated automatically by a consumer.
            fixed: If True, the date is not updated automatically.
            data_style: The style name for formatting.
            text: The textual representation of the date.
                If not provided, it is generated from `date`.
            date_adjust: A timedelta to adjust the
                date value.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if date:
                self.date = DateTime.encode(date)
            if fixed:
                self.fixed = True
            if data_style is not None:
                self.data_style = data_style
            if text is None and date is not None:
                text = Date.encode(date)
            self.text = text
            if date_adjust is not None:
                self.date_adjust = Duration.encode(date_adjust)


VarDate._define_attribut_property()


class VarTime(Element):
    """A time field, "text:time".

    Displays a time, which can be fixed or automatically updated.

    Attributes:
        time (str): The time value in ISO 8601 format.
        fixed (bool): If True, the time is not updated automatically.
        data_style (str): The style for formatting the time.
        time_adjust (str): A duration to add to or subtract from the time.
    """

    _tag = "text:time"
    _properties = (
        PropDef("time", "text:time-value"),
        PropDef("fixed", "text:fixed"),
        PropDef("data_style", "style:data-style-name"),
        PropDef("time_adjust", "text:time-adjust"),
    )

    def __init__(
        self,
        time: datetime | dt_time | None = None,
        fixed: bool = False,
        data_style: str | None = None,
        text: str | None = None,
        time_adjust: timedelta | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarTime element.

        Args:
            time: The time value. Defaults to
                the current time.
            fixed: If True, the time is not updated automatically.
            data_style: The style name for formatting.
            text: The textual representation of the time.
                If not provided, it is generated from `time`.
            time_adjust: A timedelta to adjust the
                time value.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if time is None:
                time = dt_time()
            if isinstance(time, dt_time):
                # need convert to datetime
                time = datetime(
                    year=1900,
                    month=1,
                    day=1,
                    hour=time.hour,
                    minute=time.minute,
                    second=time.second,
                )
            self.time = DateTime.encode(time)
            if fixed:
                self.fixed = True
            if data_style is not None:
                self.data_style = data_style
            if text is None:
                text = time.strftime("%H:%M:%S")
            self.text = text
            if time_adjust is not None:
                self.time_adjust = Duration.encode(time_adjust)


VarTime._define_attribut_property()


class VarChapter(Element):
    """A chapter field, "text:chapter".

    Displays information about the current chapter, such as its name or
    number.

    Attributes:
        display (str): The format for displaying the chapter information
            (e.g., 'name', 'number', 'number-and-name').
        outline_level (str): The heading level to consider for the chapter
            information.
    """

    _tag = "text:chapter"
    _properties = (
        PropDef("display", "text:display"),
        PropDef("outline_level", "text:outline-level"),
    )
    DISPLAY_VALUE_CHOICE: ClassVar = {
        "number",
        "name",
        "number-and-name",
        "plain-number",
        "plain-number-and-name",
    }

    def __init__(
        self,
        display: str | None = "name",
        outline_level: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarChapter element.

        Args:
            display: The format for the chapter information.
                Can be 'name' (default), 'number', 'number-and-name', etc.
            outline_level: The heading outline level to use
                for chapter context.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if display not in VarChapter.DISPLAY_VALUE_CHOICE:
                raise ValueError(f"Unknown display value: '{display}'")
            self.display = display
            if outline_level is not None:
                self.outline_level = outline_level


VarChapter._define_attribut_property()


class VarFileName(Element):
    """A file name field, "text:file-name".

    Displays the file name of the document, with different formatting
    options.

    Attributes:
        display (str): The format for the file name ('full', 'path', 'name',
            'name-and-extension').
        fixed (bool): If True, the file name is not updated automatically.
    """

    _tag = "text:file-name"
    _properties = (
        PropDef("display", "text:display"),
        PropDef("fixed", "text:fixed"),
    )
    DISPLAY_VALUE_CHOICE: ClassVar = {
        "full",
        "path",
        "name",
        "name-and-extension",
    }

    def __init__(
        self,
        display: str | None = "full",
        fixed: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarFileName element.

        Args:
            display: The format for the file name. Can be
                'full' (default), 'path', 'name', or 'name-and-extension'.
            fixed: If True, the field is not updated automatically.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if display not in VarFileName.DISPLAY_VALUE_CHOICE:
                raise ValueError(f"Unknown display value: '{display}'")
            self.display = display
            if fixed:
                self.fixed = True


VarFileName._define_attribut_property()


class VarInitialCreator(Element):
    """An initial creator field, "text:initial-creator".

    Displays the name of the person who initially created the document, based
    on the document's metadata.

    Attributes:
        fixed (bool): If True, the field is not updated automatically.
    """

    _tag = "text:initial-creator"
    _properties = (PropDef("fixed", "text:fixed"),)

    def __init__(self, fixed: bool = False, **kwargs: Any) -> None:
        """Initializes the VarInitialCreator element.

        Args:
            fixed: If True, the field is not updated automatically.
        """
        super().__init__(**kwargs)
        if self._do_init and fixed:
            self.fixed = True


VarInitialCreator._define_attribut_property()


class VarCreationDate(Element):
    """A creation date field, "text:creation-date".

    Displays the date the document was created, based on metadata.

    Attributes:
        fixed (bool): If True, the field is not updated automatically.
        data_style (str): The style for formatting the date.
    """

    _tag = "text:creation-date"
    _properties = (
        PropDef("fixed", "text:fixed"),
        PropDef("data_style", "style:data-style-name"),
    )

    def __init__(
        self,
        fixed: bool = False,
        data_style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarCreationDate element.

        Args:
            fixed: If True, the field is not updated automatically.
            data_style: The style name for formatting.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationDate._define_attribut_property()


class VarCreationTime(Element):
    """A creation time field, "text:creation-time".

    Displays the time the document was created, based on metadata.

    Attributes:
        fixed (bool): If True, the field is not updated automatically.
        data_style (str): The style for formatting the time.
    """

    _tag = "text:creation-time"
    _properties = (
        PropDef("fixed", "text:fixed"),
        PropDef("data_style", "style:data-style-name"),
    )

    def __init__(
        self,
        fixed: bool = False,
        data_style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the VarCreationTime element.

        Args:
            fixed: If True, the field is not updated automatically.
            data_style: The style name for formatting.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationTime._define_attribut_property()


class VarDescription(VarInitialCreator):
    """A description field, "text:description".

    Displays the document's description (or comments) from its metadata.
    """

    _tag = "text:description"


VarDescription._define_attribut_property()


class VarTitle(VarInitialCreator):
    """A title field, "text:title".

    Displays the document's title from its metadata.
    """

    _tag = "text:title"


VarTitle._define_attribut_property()


class VarSubject(VarInitialCreator):
    """A subject field, "text:subject".

    Displays the document's subject from its metadata.
    """

    _tag = "text:subject"


VarSubject._define_attribut_property()


class VarKeywords(VarInitialCreator):
    """A keywords field, "text:keywords".

    Displays the document's keywords from its metadata.
    """

    _tag = "text:keywords"


VarKeywords._define_attribut_property()

register_element_class(VarSet)
register_element_class(VarGet)
register_element_class(VarPageNumber)
register_element_class(VarPageCount)
register_element_class(VarDate)
register_element_class(VarTime)
register_element_class(VarChapter)
register_element_class(VarFileName)
register_element_class(VarInitialCreator)
register_element_class(VarCreationDate)
register_element_class(VarCreationTime)
register_element_class(VarDescription)
register_element_class(VarTitle)
register_element_class(VarSubject)
register_element_class(VarKeywords)
