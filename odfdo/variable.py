# Copyright 2018-2020 Jérôme Dumonteil
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
"""User fields and variable fields classes
"""
from .datatype import Date, DateTime, Duration
from .const import ODF_META
from .utils import _set_value_and_type
from .element import Element, register_element_class


class VarDecls(Element):
    _tag = "text:variable-decls"


class VarDecl(Element):
    _tag = "text:variable-decl"
    _properties = (("name", "text:name"), ("value_type", "office:value-type"))

    def __init__(self, name=None, value_type=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            if value_type:
                self.value_type = value_type


VarDecl._define_attribut_property()


class VarSet(Element):
    _tag = "text:variable-set"
    _properties = (
        ("name", "text:name"),
        ("style", "style:data-style-name"),
        ("display", "text:display"),
    )

    def __init__(
        self,
        name=None,
        value=None,
        value_type=None,
        display=False,
        text=None,
        style=None,
        **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            text = _set_value_and_type(
                self, value=value, value_type=value_type, text=text
            )
            if not display:
                self.display = "none"
            else:
                self.text = text


VarSet._define_attribut_property()


class VarGet(Element):
    _tag = "text:variable-get"
    _properties = (("name", "text:name"), ("style", "style:data-style-name"))

    def __init__(
        self, name=None, value=None, value_type=None, text=None, style=None, **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            text = _set_value_and_type(
                self, value=value, value_type=value_type, text=text
            )
            self.text = text


VarGet._define_attribut_property()


class UserFieldDecls(Element):
    _tag = "text:user-field-decls"


class UserFieldDecl(Element):
    _tag = "text:user-field-decl"
    _properties = (("name", "text:name"),)

    def __init__(self, name=None, value=None, value_type=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            _set_value_and_type(self, value=value, value_type=value_type)


UserFieldDecl._define_attribut_property()


class UserFieldGet(Element):
    _tag = "text:user-field-get"
    _properties = (("name", "text:name"), ("style", "style:data-style-name"))

    def __init__(
        self, name=None, value=None, value_type=None, text=None, style=None, **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            text = _set_value_and_type(
                self, value=value, value_type=value_type, text=text
            )
            self.text = text
            if style:
                self.style = style


UserFieldGet._define_attribut_property()


class UserFieldInput(UserFieldGet):
    _tag = "text:user-field-input"


UserFieldInput._define_attribut_property()


class UserDefined(Element):
    """Return a user defined field "text:user-defined". If the current
    document is provided, try to extract the content of the meta user defined
    field of same name.

    Arguments:

        name -- str, name of the user defined field

        value -- python typed value, value of the field

        value_type -- str, office:value-type known type

        text -- str

        style -- str

        from_document -- ODF document
    """

    _tag = "text:user-defined"
    _properties = (("name", "text:name"), ("style", "style:data-style-name"))

    def __init__(
        self,
        name=None,
        value=None,
        value_type=None,
        text=None,
        style=None,
        from_document=None,
        **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if from_document is not None:
                meta_infos = from_document.get_part(ODF_META)
                if meta_infos is not None:
                    content = meta_infos.get_user_defined_metadata_of_name(name)
                    if content is not None:
                        value = content.get("value", None)
                        value_type = content.get("value_type", None)
                        text = content.get("text", None)
            text = _set_value_and_type(
                self, value=value, value_type=value_type, text=text
            )
            self.text = text


UserDefined._define_attribut_property()


class VarPageNumber(Element):
    """
    select_page -- string in ('previous', 'current', 'next')

    page_adjust -- int (to add or subtract to the page number)
    """

    _tag = "text:page-number"
    _properties = (
        ("select_page", "text:select-page"),
        ("page_adjust", "text:page-adjust"),
    )

    def __init__(self, select_page=None, page_adjust=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if select_page is None:
                select_page = "current"
            self.select_page = select_page
            if page_adjust is not None:
                self.page_adjust = page_adjust


VarPageNumber._define_attribut_property()


class VarPageCount(Element):
    _tag = "text:page-count"


class VarDate(Element):
    _tag = "text:date"
    _properties = (
        ("date", "text:date-value"),
        ("fixed", "text:fixed"),
        ("data_style", "style:data-style-name"),
        ("date_adjust", "text:date-adjust"),
    )

    def __init__(
        self, date=None, fixed=False, data_style=None, text=None, date_adjust=None, **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            self.date = DateTime.encode(date)
            if fixed:
                self.fixed = True
            if data_style is not None:
                self.data_style = data_style
            if text is None:
                text = Date.encode(date)
            self.text = text
            if date_adjust is not None:
                self.date_adjust = Duration.encode(date_adjust)


VarDate._define_attribut_property()


class VarTime(Element):
    _tag = "text:time"
    _properties = (
        ("time", "text:time-value"),
        ("fixed", "text:fixed"),
        ("data_style", "style:data-style-name"),
        ("time_adjust", "text:time-adjust"),
    )

    def __init__(
        self, time=None, fixed=False, data_style=None, text=None, time_adjust=None, **kw
    ):
        super().__init__(**kw)
        if self._do_init:
            self.time = DateTime.encode(time)
            if fixed:
                self.fixed = True
            if data_style is not None:
                self.data_style = data_style
            if text is None:
                text = time.strftime("%H:%M:%S")
            self.text = text
            if time_adjust is not None:
                self.date_adjust = Duration.encode(time_adjust)


VarTime._define_attribut_property()


class VarChapter(Element):
    _tag = "text:chapter"
    _properties = (("display", "text:display"), ("outline_level", "text:outline-level"))
    display_value_choice = {
        "number",
        "name",
        "number-and-name",
        "plain-number",
        "plain-number-and-name",
    }

    def __init__(self, display="name", outline_level=None, **kw):
        """display can be: 'number', 'name', 'number-and-name', 'plain-number' or
        'plain-number-and-name'
        """
        super().__init__(**kw)
        if self._do_init:
            if display not in VarChapter.display_value_choice:
                raise ValueError("unknown display value: %s" % display)
            self.display = display
            if outline_level is not None:
                self.outline_level = outline_level


VarChapter._define_attribut_property()


class VarFileName(Element):
    _tag = "text:file-name"
    _properties = (("display", "text:display"), ("fixed", "text:fixed"))
    display_value_choice = {"full", "path", "name", "name-and-extension"}

    def __init__(self, display="full", fixed=False, **kw):
        """display can be: 'full', 'path', 'name' or 'name-and-extension'"""
        super().__init__(**kw)
        if self._do_init:
            if display not in VarFileName.display_value_choice:
                raise ValueError("unknown display value: %s" % display)
            self.display = display
            if fixed:
                self.fixed = True


VarFileName._define_attribut_property()


class VarInitialCreator(Element):
    _tag = "text:initial-creator"
    _properties = (("fixed", "text:fixed"),)

    def __init__(self, fixed=False, **kw):
        super().__init__(**kw)
        if self._do_init:
            if fixed:
                self.fixed = True


VarInitialCreator._define_attribut_property()


class VarCreationDate(Element):
    _tag = "text:creation-date"
    _properties = (("fixed", "text:fixed"), ("data_style", "style:data-style-name"))

    def __init__(self, fixed=False, data_style=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationDate._define_attribut_property()


class VarCreationTime(Element):
    _tag = "text:creation-time"
    _properties = (("fixed", "text:fixed"), ("data_style", "style:data-style-name"))

    def __init__(self, fixed=False, data_style=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if fixed:
                self.fixed = True
            if data_style:
                self.data_style = data_style


VarCreationTime._define_attribut_property()


class VarDescription(VarInitialCreator):
    _tag = "text:description"


VarDescription._define_attribut_property()


class VarTitle(VarInitialCreator):
    _tag = "text:title"


VarTitle._define_attribut_property()


class VarSubject(VarInitialCreator):
    _tag = "text:subject"


VarSubject._define_attribut_property()


class VarKeywords(VarInitialCreator):
    _tag = "text:keywords"


VarKeywords._define_attribut_property()

register_element_class(VarDecls)
register_element_class(VarDecl)
register_element_class(VarSet)
register_element_class(VarGet)
register_element_class(UserFieldDecls)
register_element_class(UserFieldDecl)
register_element_class(UserFieldGet)
register_element_class(UserFieldInput)
register_element_class(UserDefined)
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
