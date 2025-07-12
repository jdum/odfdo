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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from collections.abc import Iterable
from datetime import datetime, time, timedelta

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.variable import (
    VarChapter,
    VarCreationDate,
    VarCreationTime,
    VarDate,
    VarDecl,
    VarDecls,
    VarDescription,
    VarFileName,
    VarGet,
    VarInitialCreator,
    VarKeywords,
    VarPageCount,
    VarPageNumber,
    VarSet,
    VarSubject,
    VarTime,
    VarTitle,
)

ZOE = "你好 Zoé"


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("variable.odt"))
    yield document


def test_var_decls_class():
    variable = VarDecls()
    assert isinstance(variable, VarDecls)


def test_var_decl_class():
    variable = VarDecl()
    assert isinstance(variable, VarDecl)


def test_var_set_class():
    variable = VarSet()
    assert isinstance(variable, VarSet)


def test_var_set_arg_style():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    assert variable.style == "some_bold"


def test_var_set_style_keep():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    variable.set_value(55)
    assert variable.style == "some_bold"


def test_var_set_display_deleted():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    variable.display = None
    variable.set_value(55)
    assert variable.display is None


def test_var_set_display_keep_true():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    variable.display = True
    variable.set_value(55)
    assert variable.display is True


def test_var_set_display_keep_false():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    variable.display = False
    variable.set_value(55)
    assert variable.display is False


def test_var_set_display_no_text():
    variable = VarSet(name="myvar", value=42, style="some_bold")
    variable.display = "none"
    variable.set_value(None)
    assert variable.text == ""


def test_var_get_class():
    variable = VarGet()
    assert isinstance(variable, VarGet)


def test_var_get_arg_style():
    variable = VarGet(name="myvar", style="some_bold")
    assert variable.style == "some_bold"


def test_var_get_arg_from_tag():
    variable = Element.from_tag(
        '<text:variable-get text:name="myvar" style:data-style-name="some_bold">'
        "</text:variable-get>"
    )
    assert isinstance(variable, VarGet)


def test_var_get_arg_from_tag2():
    variable = Element.from_tag(
        '<text:variable-get text:name="myvar" style:data-style-name="some_bold">'
        "</text:variable-get>"
    )
    assert variable.style == "some_bold"
    assert variable.name == "myvar"
    assert not variable.text


def test_var_page_number_class():
    variable = VarPageNumber()
    assert isinstance(variable, VarPageNumber)


def test_var_page_number_from_tag():
    variable = Element.from_tag('<text:page-number text:select-page="current"/>')
    assert isinstance(variable, VarPageNumber)


def test_var_page_number_from_tag2():
    variable = Element.from_tag('<text:page-number text:select-page="current"/>')
    assert variable.select_page == "current"


def test_var_page_count_class():
    variable = VarPageCount()
    assert isinstance(variable, VarPageCount)


def test_var_date_class():
    variable = VarDate()
    assert isinstance(variable, VarDate)


def test_var_date_from_tag():
    variable = Element.from_tag("<text:date></text:date>")
    assert isinstance(variable, VarDate)


def test_var_date_datetime():
    variable = VarDate(date=datetime(1977, 12, 25, 12, 15, 10), data_style="date_style")
    assert variable.date == "1977-12-25T12:15:10"


def test_var_date_style():
    variable = VarDate(date=datetime(1977, 12, 25, 12, 15, 10), data_style="date_style")
    assert variable.data_style == "date_style"


def test_var_date_adjust():
    variable = VarDate(
        date=datetime(1977, 12, 25, 12, 15, 10), date_adjust=timedelta(hours=2)
    )
    assert variable.date_adjust == "PT02H00M00S"


def test_var_time_class():
    variable = VarTime()
    assert isinstance(variable, VarTime)


def test_var_time_from_tag():
    variable = Element.from_tag(
        '<text:time text:time-value="1977-12-25T12:15:10">12:15:10</text:time>'
    )
    assert isinstance(variable, VarTime)


def test_var_time_style():
    variable = VarTime(data_style="date_style")
    assert variable.data_style == "date_style"


def test_var_time_adjust():
    variable = VarTime(time_adjust=timedelta(hours=2))
    assert variable.time_adjust == "PT02H00M00S"


def test_var_chapter_class():
    variable = VarChapter()
    assert isinstance(variable, VarChapter)


def test_var_chapter_from_tag():
    variable = Element.from_tag('<text:chapter text:display="name"/>')
    assert isinstance(variable, VarChapter)


def test_var_chapter_wrong_display():
    with pytest.raises(ValueError):
        VarChapter(display="wrong")


def test_var_file_name_class():
    variable = VarFileName()
    assert isinstance(variable, VarFileName)


def test_var_file_name_from_tag():
    variable = Element.from_tag(
        '<text:file-name text:display="name-and-extension">file.odt</text:file-name>'
    )
    assert isinstance(variable, VarFileName)


def test_var_file_name_from_tag2():
    variable = Element.from_tag(
        '<text:file-name text:display="name-and-extension">file.odt</text:file-name>'
    )
    assert variable.text == "file.odt"


def test_var_file_name_wrong_display():
    with pytest.raises(ValueError):
        VarFileName(display="wrong")


def test_var_initial_creator_class():
    variable = VarInitialCreator()
    assert isinstance(variable, VarInitialCreator)


def test_var_initial_creator_from_tag():
    variable = Element.from_tag(
        '<text:initial-creator text:fixed="true">John Doe</text:initial-creator>'
    )
    assert isinstance(variable, VarInitialCreator)


def test_var_initial_creator_from_tag2():
    variable = Element.from_tag(
        '<text:initial-creator text:fixed="true">John Doe</text:initial-creator>'
    )
    assert variable.text == "John Doe"


def test_var_initial_creator_fixed():
    variable = VarInitialCreator(fixed=True)
    assert variable.fixed is True


def test_var_creation_date_class():
    variable = VarCreationDate()
    assert isinstance(variable, VarCreationDate)


def test_var_creation_date_from_tag():
    variable = Element.from_tag("<text:creation-date/>")
    assert isinstance(variable, VarCreationDate)


def test_var_creation_date_fixed():
    variable = VarCreationDate(fixed=True)
    assert variable.fixed is True


def test_var_creation_date_data_style():
    variable = VarCreationDate(data_style="some_style")
    assert variable.data_style == "some_style"


def test_var_creation_time_class():
    variable = VarCreationTime()
    assert isinstance(variable, VarCreationTime)


def test_var_creation_time_from_tag():
    variable = Element.from_tag("<text:creation-time/>")
    assert isinstance(variable, VarCreationTime)


def test_var_creation_time_fixed():
    variable = VarCreationTime(fixed=True)
    assert variable.fixed is True


def test_var_creation_time_data_style():
    variable = VarCreationTime(data_style="some_style")
    assert variable.data_style == "some_style"


def test_var_description_class():
    variable = VarDescription()
    assert isinstance(variable, VarDescription)


def test_var_title_class():
    variable = VarTitle()
    assert isinstance(variable, VarTitle)


def test_var_subject_class():
    variable = VarSubject()
    assert isinstance(variable, VarSubject)


def test_var_keywords_class():
    variable = VarKeywords()
    assert isinstance(variable, VarKeywords)


def test_create_variable_decl():
    variable_decl = VarDecl(ZOE, "float")
    assert variable_decl.serialize() in (
        (f'<text:variable-decl text:name="{ZOE}" office:value-type="float"/>'),
        (f'<text:variable-decl office:value-type="float" text:name="{ZOE}"/>'),
    )


def test_create_variable_set_float():
    variable_set = VarSet(ZOE, value=42)
    expected = (
        f'<text:variable-set text:name="{ZOE}" '
        'office:value-type="float" calcext:value-type="float" '
        'office:value="42" calcext:value="42" '
        'text:display="none"/>'
    )
    assert variable_set.serialize() == expected


def test_create_variable_set_datetime():
    date = datetime(2009, 5, 17, 23, 23, 00)
    variable_set = VarSet(ZOE, value=date, display=True)
    expected = (
        f'<text:variable-set text:name="{ZOE}" '
        'office:value-type="date" calcext:value-type="date" '
        'office:date-value="2009-05-17T23:23:00">'
        "2009-05-17T23:23:00"
        "</text:variable-set>"
    )
    assert variable_set.serialize() == expected


def test_create_variable_get():
    variable_get = VarGet(ZOE, value=42)
    expected = (
        f'<text:variable-get text:name="{ZOE}" '
        'office:value-type="float" calcext:value-type="float" '
        'office:value="42" calcext:value="42">'
        "42"
        "</text:variable-get>"
    )
    assert variable_get.serialize() == expected


def test_get_variable_decl(document):
    body = document.body
    name = "Variabilité"
    variable_decl = body.get_variable_decl(name)
    expected = f'<text:variable-decl office:value-type="float" text:name="{name}"/>'
    assert variable_decl.serialize() == expected


def test_get_variable_set(document):
    body = document.body
    name = "Variabilité"
    variable_sets = body.get_variable_sets(name)
    assert len(variable_sets) == 1
    expected = (
        f'<text:variable-set text:name="{name}" '
        'office:value-type="float" office:value="123" '
        'style:data-style-name="N1">123</text:variable-set>'
    )
    assert variable_sets[0].serialize() == expected


def test_get_variable_get(document):
    body = document.body
    value = body.get_variable_set_value("Variabilité")
    assert value == 123


# TODO On all the following variable tests, interact with the document


def test_create_page_number():
    page_number = VarPageNumber()
    expected = '<text:page-number text:select-page="current"/>'
    assert page_number.serialize() == expected


def test_create_page_number_complex():
    page_number = VarPageNumber(select_page="next", page_adjust=1)
    expected = '<text:page-number text:select-page="next" text:page-adjust="1"/>'
    assert page_number.serialize() == expected


def test_create_page_count():
    page_count = VarPageCount()
    expected = "<text:page-count/>"
    assert page_count.serialize() == expected


def test_create_date():
    date_element = VarDate(datetime(2009, 7, 20))
    expected = '<text:date text:date-value="2009-07-20T00:00:00">2009-07-20</text:date>'
    assert date_element.serialize() == expected


def test_create_date_fixed():
    date_element = VarDate(datetime(2009, 7, 20), fixed=True)
    expected = (
        '<text:date text:date-value="2009-07-20T00:00:00" '
        'text:fixed="true">'
        "2009-07-20"
        "</text:date>"
    )
    assert date_element.serialize() == expected


def test_create_date_text():
    date_element = VarDate(datetime(2009, 7, 20), text="20 juil. 09")
    expected = (
        '<text:date text:date-value="2009-07-20T00:00:00">20 juil. 09</text:date>'
    )
    assert date_element.serialize() == expected


def test_create_time_empty():
    time_element = VarTime()
    expected = '<text:time text:time-value="1900-01-01T00:00:00">00:00:00</text:time>'
    assert time_element.serialize() == expected


def test_create_time():
    time_element = VarTime(time(19, 30))
    expected = '<text:time text:time-value="1900-01-01T19:30:00">19:30:00</text:time>'
    assert time_element.serialize() == expected


def test_create_time_datetime():
    time_element = VarTime(datetime(2024, 2, 25, 19, 30, 15))
    expected = '<text:time text:time-value="2024-02-25T19:30:15">19:30:15</text:time>'
    assert time_element.serialize() == expected


def test_create_time_fixed():
    time_element = VarTime(time(19, 30), fixed=True)
    expected = (
        '<text:time text:time-value="1900-01-01T19:30:00" '
        'text:fixed="true">'
        "19:30:00"
        "</text:time>"
    )
    assert time_element.serialize() == expected


def test_create_time_text():
    time_element = VarTime(time(19, 30), text="19h30")
    expected = '<text:time text:time-value="1900-01-01T19:30:00">19h30</text:time>'
    assert time_element.serialize() == expected


def test_create_chapter():
    chapter = VarChapter()
    expected = '<text:chapter text:display="name"/>'
    assert chapter.serialize() == expected


def test_create_chapter_complex():
    chapter = VarChapter(display="number-and-name", outline_level=1)
    expected = '<text:chapter text:display="number-and-name" text:outline-level="1"/>'
    assert chapter.serialize() == expected


def test_create_filename():
    filename = VarFileName()
    expected = '<text:file-name text:display="full"/>'
    assert filename.serialize() == expected


def test_create_filename_fixed():
    filename = VarFileName(fixed=True)
    expected = '<text:file-name text:display="full" text:fixed="true"/>'
    assert filename.serialize() == expected


def test_create_initial_creator():
    element = VarInitialCreator()
    expected = "<text:initial-creator/>"
    assert element.serialize() == expected


def test_create_creation_date():
    element = VarCreationDate()
    expected = "<text:creation-date/>"
    assert element.serialize() == expected


def test_create_creation_time():
    element = VarCreationTime()
    expected = "<text:creation-time/>"
    assert element.serialize() == expected


def test_create_description():
    element = VarDescription()
    expected = "<text:description/>"
    assert element.serialize() == expected


def test_create_title():
    element = VarTitle()
    expected = "<text:title/>"
    assert element.serialize() == expected


def test_create_subject():
    element = VarSubject()
    expected = "<text:subject/>"
    assert element.serialize() == expected


def test_create_keywords():
    element = VarKeywords()
    expected = "<text:keywords/>"
    assert element.serialize() == expected
