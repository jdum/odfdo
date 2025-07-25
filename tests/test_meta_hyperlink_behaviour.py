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


from odfdo.meta_hyperlink_behaviour import MetaHyperlinkBehaviour


def test_create_minimal():
    behaviour = MetaHyperlinkBehaviour()
    expected = '<meta:hyperlink-behaviour office:target-frame-name="_blank" xlink:show="replace"/>'
    assert behaviour.serialize() == expected
    assert behaviour.show == "replace"


def test_create():
    behaviour = MetaHyperlinkBehaviour(target_frame_name="some_frame", show="_top")
    expected = '<meta:hyperlink-behaviour office:target-frame-name="some_frame" xlink:show="_top"/>'
    assert behaviour.serialize() == expected
    assert behaviour.show == "_top"
    assert behaviour.target_frame_name == "some_frame"
    assert repr(behaviour) == (
        "<MetaHyperlinkBehaviour tag=meta:hyperlink-behaviour target=some_frame show=_top>"
    )


def test_as_dict():
    behaviour = MetaHyperlinkBehaviour(target_frame_name="some_frame", show="_top")
    expected = {
        "office:target-frame-name": "some_frame",
        "xlink:show": "_top",
    }
    assert behaviour.as_dict() == expected


def test_str():
    behaviour = MetaHyperlinkBehaviour(target_frame_name="some_frame", show="_top")
    expected = "(some_frame)"
    assert str(behaviour) == expected
