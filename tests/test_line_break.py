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


from odfdo.line_break import LineBreak


def test_create_line_break():
    lb = LineBreak()
    expected = "<text:line-break/>"
    assert lb.serialize() == expected


def test_create_line_break_str():
    lb = LineBreak()
    assert str(lb) == "\n"


def test_line_break_getter_0():
    lb = LineBreak()
    expected = "<text:line-break/>"
    assert lb.serialize() == expected


def test_line_break_getter_1():
    lb = LineBreak()
    assert lb.text == "\n"


def test_line_break_setter():
    lb = LineBreak()
    lb.text = "x"
    assert lb.text == "\n"
