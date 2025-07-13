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
from datetime import datetime

from odfdo.datatype import DateTime
from odfdo.meta_template import MetaTemplate


def test_repr():
    template = MetaTemplate(href="http://exemple.com")
    assert repr(template) == "<MetaTemplate tag=meta:template href=http://exemple.com>"


def test_str_1():
    template = MetaTemplate(href="http://exemple.com")
    assert str(template) == "(http://exemple.com)"


def test_str_2():
    template = MetaTemplate(href="http://exemple.com", title="Example")
    assert str(template) == "[Example](http://exemple.com)"


def test_create_empty():
    template = MetaTemplate()
    expected = '<meta:template xlink:actuate="onRequest" xlink:type="simple" meta:date='
    assert template.serialize().startswith(expected)
    assert template.href == ""
    assert template.title == ""


def test_create():
    now = datetime.now().replace(microsecond=0)
    template = MetaTemplate(date=now, href="some url", title="some title")
    expected = '<meta:template xlink:actuate="onRequest" xlink:type="simple" meta:date='
    assert template.serialize().startswith(expected)
    assert template.date == DateTime.encode(now)
    assert template.href == "some url"
    assert template.title == "some title"


def test_as_dict():
    dt = datetime(2024, 1, 31, 14, 59, 0).replace(microsecond=0)
    template = MetaTemplate(date=dt, href="some url", title="some title")
    expected = {
        "meta:date": "2024-01-31T14:59:00",
        "xlink:actuate": "onRequest",
        "xlink:href": "some url",
        "xlink:title": "some title",
        "xlink:type": "simple",
    }
    assert template.as_dict() == expected
