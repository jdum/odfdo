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

from odfdo.utils import oooc_to_ooow


def test_addition():
    formula = "oooc:=[.A2]+[.A3]"
    excepted = "ooow:<A2>+<A3>"
    assert oooc_to_ooow(formula) == excepted


def test_sum():
    formula = "oooc:=SUM([.B2:.B4])"
    excepted = "ooow:sum <B2:B4>"
    assert oooc_to_ooow(formula) == excepted


def test_addition_sum():
    formula = "oooc:=[.A2]-[.A3]+SUM([.B2:.B4])*[.D4]"
    excepted = "ooow:<A2>-<A3>+sum <B2:B4>*<D4>"
    assert oooc_to_ooow(formula) == excepted
