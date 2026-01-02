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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.paragraph import Paragraph
from odfdo.spacer import Spacer


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("base_text.odt"))
    yield document


def test_read_spacer_empty():
    element = Element.from_tag("<text:s />")
    assert isinstance(element, Spacer)
    assert element.length == 1


def test_read_spacer_empty_str():
    element = Element.from_tag("<text:s />")
    assert str(element) == " "


def test_read_spacer_1():
    element = Element.from_tag('<text:s text:c="1" />')
    assert isinstance(element, Spacer)
    assert element.length == 1


def test_read_spacer_1_str():
    element = Element.from_tag('<text:s text:c="1" />')
    assert str(element) == " "


def test_read_spacer_2():
    element = Element.from_tag('<text:s text:c="2" />')
    assert isinstance(element, Spacer)
    assert element.length == 2


def test_read_spacer_2_str():
    element = Element.from_tag('<text:s text:c="2" />')
    assert str(element) == "  "


def test_create_space_1_base():
    sp1 = Spacer()
    expected = "<text:s/>"
    assert sp1.serialize() == expected


def test_create_space_1_number():
    sp1 = Spacer()
    assert sp1.number in (None, "1")


def test_create_space_1_length():
    sp1 = Spacer()
    assert sp1.length == 1


def test_create_space_1_length_mod_serialize():
    sp1 = Spacer()
    sp1.length = 3
    expected = '<text:s text:c="3"/>'
    assert sp1.serialize() == expected


def test_create_space_1_length_mod_number():
    sp1 = Spacer()
    sp1.length = 3
    assert sp1.number == "3"


def test_create_space_1_length_mod_length():
    sp1 = Spacer()
    sp1.length = 3
    assert sp1.length == 3


def test_create_space_5_base():
    sp1 = Spacer(5)
    expected = '<text:s text:c="5"/>'
    assert sp1.serialize() == expected


def test_create_space_5_number():
    sp1 = Spacer(5)
    assert sp1.number == "5"


def test_create_space_5_length():
    sp1 = Spacer(5)
    assert sp1.length == 5


def test_create_spaces():
    sp5 = Spacer(5)
    expected = '<text:s text:c="5"/>'
    assert sp5.serialize() == expected


def test_create_naive_spaces():
    para = Paragraph("   ")
    # old rules
    # expected = '<text:p> <text:s text:c="2"/></text:p>'
    expected = '<text:p><text:s text:c="3"/></text:p>'
    assert para.serialize() == expected


def test_create_naive_spaces_no_format():
    para = Paragraph("   ", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_create_naive_cr_no_format():
    para = Paragraph("\n", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_plain_text_splitted_elements_spaces():
    txt = "A test,\n   \twith \n\n some é and \t and     5 spaces."
    para = Paragraph()
    content = para._expand_spaces(txt)
    content = para._merge_spaces(content)
    content = para._replace_tabs_lb(content)
    assert isinstance(content[3], Spacer)


def test_paragraph_1_space():
    para = Paragraph(" ")
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_2_spaces():
    para = Paragraph("  ")
    # new rule
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_paragraph_1_space_no_format():
    para = Paragraph(" ", formatted=False)
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_2_spaces_no_format():
    para = Paragraph("  ", formatted=False)
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_paragraph_any_spaces_no_format():
    para = Paragraph("  \n\t ", formatted=False)
    # new rule
    expected = "<text:p><text:s/></text:p>"
    assert para.serialize() == expected


def test_space_plus_space():
    para = Paragraph(" ")
    para.append(" ")
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_space_plus_space_no_format():
    para = Paragraph(" ")
    para.append(" ", formatted=False)
    expected = '<text:p><text:s text:c="2"/></text:p>'
    assert para.serialize() == expected


def test_spacer_setter_0():
    spacer = Spacer()
    spacer.text = None
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_1():
    spacer = Spacer()
    spacer.text = ""
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_2():
    spacer = Spacer()
    spacer.text = "x"
    expected = "<text:s/>"
    assert spacer.serialize() == expected


def test_spacer_setter_3():
    spacer = Spacer()
    spacer.text = "xx"
    expected = '<text:s text:c="2"/>'
    assert spacer.serialize() == expected


def test_spacer_setter_4():
    spacer = Spacer()
    spacer.text = "xxx"
    expected = '<text:s text:c="3"/>'
    assert spacer.serialize() == expected
