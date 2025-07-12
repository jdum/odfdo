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
"""Variable fields classes."""

from __future__ import annotations

from datetime import datetime, timedelta
from datetime import time as dt_time
from typing import Any, ClassVar

from .datatype import Date, DateTime, Duration
from .element import Element, PropDef, register_element_class
from .element_typed import ElementTyped
from .user_field import (  # noqa: F401
    UserDefined,
    UserFieldDecl,
    UserFieldDecls,
    UserFieldGet,
    UserFieldInput,
)


class VarDecls(Element):
    """Container of variables declarations, "text:variable-decls"."""

    _tag = "text:variable-decls"


class VarDecl(Element):
    """A variable declaration, "text:variable-decl"."""

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
        """Create a variable declaration "text:variable-decl"."""
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if value_type:
                self.value_type = value_type


VarDecl._define_attribut_property()


class VarSet(ElementTyped):
    """Representation of a variable setter, "text:variable-set"."""

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
        """Create a variable setter, "text:variable-set"."""
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
    """Representation of a variable getter, "text:variable-get"."""

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
        """Create a variable getter "text:variable-get"."""
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
    """Variable for page number, "text:page-number"."""

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
        """Create a variable for page number "text:page-number".

        select_page -- string in ('previous', 'current', 'next')

        page_adjust -- int (to add or subtract to the page number)
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
    """Variable for page count, "text:page-count"."""

    _tag = "text:page-count"


class VarDate(Element):
    """Variable for a date, "text:date"."""

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
        """create avariable for a date "text:date"."""
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
    """Variable for a time, "text:time"."""

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
        """Create a variable for a time "text:time"."""
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
    """Variable for a chapter, "text:chapter"."""

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
        """Create a variable for a chapter "text:chapter".

        display can be: 'number', 'name', 'number-and-name', 'plain-number' or
        'plain-number-and-name'
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
    """Variable for the file name, "text:file-name"."""

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
        """Create a variable for the file name "text:file-name".

        display can be: 'full', 'path', 'name' or 'name-and-extension'
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
    """Variable for the initial creator, "text:initial-creator"."""

    _tag = "text:initial-creator"
    _properties = (PropDef("fixed", "text:fixed"),)

    def __init__(self, fixed: bool = False, **kwargs: Any) -> None:
        """Create a variable for the initial creator "text:initial-creator"."""
        super().__init__(**kwargs)
        if self._do_init and fixed:
            self.fixed = True


VarInitialCreator._define_attribut_property()


class VarCreationDate(Element):
    """Variable for the creation date, "text:creation-date"."""

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
        """Create a variable for the creation date "text:creation-date"."""
        super().__init__(**kwargs)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationDate._define_attribut_property()


class VarCreationTime(Element):
    """Variable for the creation time, "text:creation-time"."""

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
        """Create a variable for the creation time "text:creation-time"."""
        super().__init__(**kwargs)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationTime._define_attribut_property()


class VarDescription(VarInitialCreator):
    """Variable for the text description, "text:description"."""

    _tag = "text:description"


VarDescription._define_attribut_property()


class VarTitle(VarInitialCreator):
    """Variable for the title, "text:title"."""

    _tag = "text:title"


VarTitle._define_attribut_property()


class VarSubject(VarInitialCreator):
    """Variable for the subject, "text:subject"."""

    _tag = "text:subject"


VarSubject._define_attribut_property()


class VarKeywords(VarInitialCreator):
    """Variable for the keywords, "text:keywords"."""

    _tag = "text:keywords"


VarKeywords._define_attribut_property()

register_element_class(VarDecls)
register_element_class(VarDecl)
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
