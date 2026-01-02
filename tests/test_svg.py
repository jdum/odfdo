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
#          David Versmisse <david.versmisse@itaapy.com>


from odfdo.element import Element
from odfdo.svg import SvgDescription, SvgTitle


def test_svg_title_class():
    title = SvgTitle()
    assert isinstance(title, SvgTitle)


def test_svg_title_minimal_tag():
    title = Element.from_tag("<svg:title/>")
    assert isinstance(title, SvgTitle)


def test_svg_title_name_init():
    title = SvgTitle("some title")
    assert title.title == "some title"


def test_svg_title_name_init_none():
    title = SvgTitle()
    assert title.title == ""


def test_svg_title_title_property():
    title = SvgTitle("first title")
    title.title = "second"
    assert title.title == "second"


def test_svg_desc_class():
    desc = SvgDescription()
    assert isinstance(desc, SvgDescription)


def test_svg_desc_minimal_tag():
    desc = Element.from_tag("<svg:desc/>")
    assert isinstance(desc, SvgDescription)


def test_svg_desc_name_init():
    desc = SvgDescription("some description")
    assert desc.description == "some description"


def test_svg_desc_name_init_none():
    desc = SvgDescription()
    assert desc.description == ""


def test_svg_desc_description_property():
    desc = SvgDescription("first description")
    desc.description = "second"
    assert desc.description == "second"
