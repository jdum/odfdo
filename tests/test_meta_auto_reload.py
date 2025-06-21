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
from datetime import timedelta

import pytest

from odfdo.datatype import Duration
from odfdo.meta_auto_reload import MetaAutoReload


def test_create_missing_arg():
    with pytest.raises(TypeError):
        _ = MetaAutoReload()


def test_create_minimal():
    delay = timedelta(seconds=15)
    reload = MetaAutoReload(delay)
    expected = (
        '<meta:auto-reload xlink:actuate="onLoad" xlink:show="replace" '
        'xlink:type="simple" meta:delay="PT00H00M15S" xlink:href=""/>'
    )
    assert reload.serialize() == expected
    assert reload.href == ""


def test_create():
    delay = timedelta(seconds=15)
    reload = MetaAutoReload(delay=delay, href="some url")
    expected = (
        '<meta:auto-reload xlink:actuate="onLoad" xlink:show="replace" '
        'xlink:type="simple" meta:delay="PT00H00M15S" xlink:href="some url"/>'
    )
    assert reload.serialize() == expected
    assert reload.delay == Duration.encode(delay)
    assert reload.href == "some url"
    assert repr(reload) == (
        "<MetaAutoReload tag=meta:auto-reload href=some url delay=0:00:15>"
    )


def test_as_dict():
    delay = timedelta(seconds=15)
    reload = MetaAutoReload(delay=delay, href="some url")
    expected = {
        "meta:delay": "PT00H00M15S",
        "xlink:actuate": "onLoad",
        "xlink:href": "some url",
        "xlink:show": "replace",
        "xlink:type": "simple",
    }
    assert reload.as_dict() == expected


def test_str():
    delay = timedelta(seconds=15)
    reload = MetaAutoReload(delay=delay, href="some url")
    expected = "(some url)"
    assert str(reload) == expected
