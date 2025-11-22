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

from odfdo.element import Element
from odfdo.meta_field import MetaField


def test_meta_field_class():
    mf = MetaField()
    assert isinstance(mf, MetaField)


def test_meta_field_minimal_tag():
    mf = Element.from_tag("<text:meta-field/>")
    assert isinstance(mf, MetaField)


def test_meta_field_repr():
    mf = MetaField()
    assert repr(mf) == "<MetaField tag=text:meta-field>"
