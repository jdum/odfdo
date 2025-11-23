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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.form import Form


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("forms.odt"))
    yield document


@pytest.fixture
def test_form() -> Iterable[Form]:
    yield Form(
        name="my form",
        command="command",
        datasource="Bibliography",
        apply_filter=False,
        command_type="table",
        control_implementation="ooo:com.sun.star.form.component.Form",
        target_frame="",
    )


def test_form_class():
    form = Form()
    assert isinstance(form, Form)


def test_form_minimal_tag():
    form = Element.from_tag("<form:form/>")
    assert isinstance(form, Form)


def test_form_serialize():
    form = Form()
    assert form.serialize() == '<form:form form:name="Form"/>'


def test_form_repr():
    form = Form()
    assert repr(form) == "<Form name=Form>"


def test_form_get_form_element_1(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert repr(form) == "<Form name=Form>"


def test_form_get_form_element_name(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.name == "Form"


def test_form_get_form_element_command(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.command == "biblio"


def test_form_get_form_element_datasource(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.datasource == "Bibliography"


def test_form_get_form_element_apply_filter(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.apply_filter is True


def test_form_get_form_element_control_implementation(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.control_implementation == "ooo:com.sun.star.form.component.Form"


def test_form_get_form_element_command_type(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.command_type == "table"


def test_form_get_form_element_target_frame(document):
    oform = document.body.office_forms
    form = oform.get_element("form:form")
    assert form.target_frame == ""


def test_form_set_form_element_1(test_form):
    assert repr(test_form) == "<Form name=my form>"


def test_form_set_form_element_2(test_form):
    #'<form:form form:name="my form"
    # form:command="command"
    # form:datasource="Bibliography"
    # form:apply-filter="false"
    # form:command-type="table"
    # form:control-implementation="ooo:com.sun.star.form.component.Form"
    # office:target-frame=""/>'
    result = test_form.serialize()
    for tag in (
        "form:name",
        "form:command",
        "form:datasource",
        "form:apply-filter",
        "form:command-type",
        "form:control-implementation",
        "office:target-frame",
    ):
        assert tag in result


def test_form_set_form_element_name(test_form):
    assert test_form.name == "my form"


def test_form_set_form_element_command(test_form):
    assert test_form.command == "command"


def test_form_set_form_element_datasource(test_form):
    assert test_form.datasource == "Bibliography"


def test_form_set_form_element_apply_filter(test_form):
    assert test_form.apply_filter is False


def test_form_set_form_element_control_implementation(test_form):
    assert test_form.control_implementation == "ooo:com.sun.star.form.component.Form"


def test_form_set_form_element_command_type(test_form):
    assert test_form.command_type == "table"


def test_form_set_form_element_target_frame(test_form):
    assert test_form.target_frame == ""


def test_form_set_no_name():
    form = Form(name=None)
    assert form.name is None
