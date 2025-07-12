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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>

from odfdo.utils import make_xpath_query


def test_element():
    query = make_xpath_query("descendant::text:p")
    assert query == "descendant::text:p"


def test_attribute():
    query = make_xpath_query("descendant::text:p", text_style="Standard")
    assert query == 'descendant::text:p[@text:style-name="Standard"]'


def test_two_attributes():
    query = make_xpath_query(
        "descendant::text:h", text_style="Standard", outline_level=1
    )
    expected = (
        'descendant::text:h[@text:outline-level="1"][@text:style-name="Standard"]'
    )
    assert query == expected


def test_position():
    query = make_xpath_query("descendant::text:h", position=1)
    assert query == "(descendant::text:h)[2]"


def test_attribute_position():
    query = make_xpath_query("descendant::text:p", text_style="Standard", position=1)
    assert query == '(descendant::text:p[@text:style-name="Standard"])[2]'


def test_two_attributes_position():
    query = make_xpath_query(
        "descendant::text:h", text_style="Standard", outline_level=1, position=1
    )
    expected = (
        '(descendant::text:h[@text:outline-level="1"][@text:style-name="Standard"])[2]'
    )
    assert query == expected


def test_case_presentation_class():
    query = make_xpath_query("descendant::text:p", presentation_class="foo")
    expected = 'descendant::text:p[@presentation:class="foo"]'
    assert query == expected


def test_case_true_arguent():
    query = make_xpath_query("descendant::text:p", change_id=True)
    expected = "descendant::text:p[@text:change-id]"
    assert query == expected


def test_case_last_arg():
    query = make_xpath_query("descendant::text:p", position=-1)
    expected = "(descendant::text:p)[last()]"
    assert query == expected


def test_case_last_2_arg():
    query = make_xpath_query("descendant::text:p", position=-2)
    expected = "(descendant::text:p)[last()-1]"
    assert query == expected
