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

from collections.abc import Iterable

import pytest

from odfdo.const import ODF_STYLES
from odfdo.document import Document
from odfdo.element import Element
from odfdo.style_containers import OfficeAutomaticStyles, OfficeMasterStyles
from odfdo.styles import Styles


@pytest.fixture
def styles(samples) -> Iterable[Styles]:
    document = Document(samples("example.odt"))
    yield document.get_part(ODF_STYLES)


def test_office_master_styles_create():
    oms = OfficeMasterStyles()
    assert oms.serialize() == "<office:master-styles/>"


def test_office_master_styles_from_tag():
    oms = Element.from_tag("<office:master-styles/>")
    assert isinstance(oms, OfficeMasterStyles)


def test_get_office_master_styles(styles):
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 1


def test_set_office_master_styles(styles):
    new_oms = OfficeMasterStyles()
    styles.office_master_styles = new_oms
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 0


def test_set_office_master_styles_no_exist(styles):
    current = styles.office_master_styles
    current.delete()
    new_oms = OfficeMasterStyles()
    styles.office_master_styles = new_oms
    oms = styles.office_master_styles
    assert isinstance(oms, OfficeMasterStyles)
    assert len(oms.children) == 0


def test_office_automatic_styles_create():
    oms = OfficeAutomaticStyles()
    assert oms.serialize() == "<office:automatic-styles/>"


def test_office_automatic_styles_from_tag():
    oms = Element.from_tag("<office:automatic-styles/>")
    assert isinstance(oms, OfficeAutomaticStyles)


def test_get_office_automatic_styles(styles):
    oas = styles.office_automatic_styles
    assert isinstance(oas, OfficeAutomaticStyles)
    assert len(oas.children) == 1


def test_set_office_automatic_styles(styles):
    new_oas = OfficeAutomaticStyles()
    styles.office_automatic_styles = new_oas
    oas = styles.office_automatic_styles
    assert isinstance(oas, OfficeAutomaticStyles)
    assert len(oas.children) == 0


def test_set_office_automatic_styles_no_exist(styles):
    current = styles.office_automatic_styles
    current.delete()
    new_oas = OfficeAutomaticStyles()
    styles.office_automatic_styles = new_oas
    oas = styles.office_automatic_styles
    assert isinstance(oas, OfficeAutomaticStyles)
    assert len(oas.children) == 0
