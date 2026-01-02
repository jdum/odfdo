# Copyright 2018-2026 Jérôme Dumonteil
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
from odfdo.office_forms import OfficeForms


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("forms.odt"))
    yield document


def test_office_forms_class():
    oform = OfficeForms()
    assert isinstance(oform, OfficeForms)


def test_office_forms_minimal_tag():
    oform = Element.from_tag("<office:forms/>")
    assert isinstance(oform, OfficeForms)


def test_office_forms_serialize():
    oform = OfficeForms()
    assert oform.serialize() == "<office:forms/>"


def test_office_forms_repr():
    oform = OfficeForms()
    assert repr(oform) == "<OfficeForms tag=office:forms>"


def test_office_forms_apply_design_mode():
    oform = OfficeForms()
    assert oform.apply_design_mode is True


def test_office_forms_apply_design_mode_false():
    oform = OfficeForms()
    oform.apply_design_mode = False
    assert oform.serialize() == '<office:forms form:apply-design-mode="false"/>'


def test_office_forms_automatic_focus():
    oform = OfficeForms()
    assert oform.automatic_focus is False


def test_office_forms_automatic_focus_true():
    oform = OfficeForms()
    oform.automatic_focus = True
    assert oform.serialize() == '<office:forms form:automatic-focus="true"/>'


def test_office_forms_get(document):
    form = document.body.get_office_forms()
    assert isinstance(form, OfficeForms)


def test_office_forms_property(document):
    form = document.body.office_forms
    assert isinstance(form, OfficeForms)
