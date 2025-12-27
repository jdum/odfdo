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

import pytest

from odfdo.frame import (
    AnchorMix,
    PosMix,
    SizeMix,
    ZMix,
    default_frame_position_style,
)
from odfdo.style import Style


def test_default_frame_position_style():
    style = default_frame_position_style()
    assert isinstance(style, Style)


def test_default_frame_position_style_detail():
    style = default_frame_position_style()
    assert style._canonicalize() == (
        '<style:style style:family="graphic" '
        'style:name="FramePosition">'
        "<style:graphic-properties "
        'style:horizontal-pos="from-left" '
        'style:horizontal-rel="paragraph" '
        'style:vertical-pos="from-top" '
        'style:vertical-rel="paragraph">'
        "</style:graphic-properties>"
        "</style:style>"
    )


def test_anchormix_minimal():
    anchor = AnchorMix()
    assert anchor._canonicalize() == (
        "<draw:anchormix-odfdo-notodf></draw:anchormix-odfdo-notodf>"
    )


def test_anchormix_type_1():
    anchor = AnchorMix()
    anchor.anchor_type = "paragraph"
    assert anchor._canonicalize() == (
        '<draw:anchormix-odfdo-notodf text:anchor-type="paragraph">'
        "</draw:anchormix-odfdo-notodf>"
    )


def test_anchormix_type_2():
    anchor = AnchorMix()
    anchor.anchor_type = "paragraph"
    assert anchor.anchor_type == "paragraph"


def test_anchormix_type_raise():
    anchor = AnchorMix()
    with pytest.raises(TypeError):
        anchor.anchor_type = "bad"


def test_anchormix_page_1():
    anchor = AnchorMix()
    anchor.anchor_type = "page"
    anchor.anchor_page = 42
    assert anchor.anchor_page == 42


def test_anchormix_page_2():
    anchor = AnchorMix()
    anchor.anchor_type = "page"
    anchor.anchor_page = 42
    anchor.anchor_page = None
    assert anchor.anchor_page is None


def test_posmix_minimal():
    pos = PosMix()
    assert pos._canonicalize() == (
        "<draw:posmixin-odfdo-notodf></draw:posmixin-odfdo-notodf>"
    )


def test_posmix_pos_1():
    pos = PosMix()
    pos.position = ("10cm", "15cm")
    assert pos._canonicalize() == (
        "<draw:posmixin-odfdo-notodf "
        'svg:x="10cm" svg:y="15cm">'
        "</draw:posmixin-odfdo-notodf>"
    )


def test_posmix_pos_2():
    pos = PosMix()
    pos.position = ("10cm", "15cm")
    assert pos.position[0] == "10cm"


def test_posmix_pos_3():
    pos = PosMix()
    pos.position = ("10cm", "15cm")
    assert pos.pos_x == "10cm"


def test_posmix_pos_4():
    pos = PosMix()
    pos.position = ("10cm", "15cm")
    assert pos.pos_y == "15cm"


def test_zmix_minimal():
    zmix = ZMix()
    assert zmix._canonicalize() == "<draw:zmix-odfdo-notodf></draw:zmix-odfdo-notodf>"


def test_zmix_1():
    zmix = ZMix()
    assert zmix.z_index is None


def test_zmix_2():
    zmix = ZMix()
    zmix.z_index = 42
    assert zmix._canonicalize() == (
        '<draw:zmix-odfdo-notodf draw:z-index="42"></draw:zmix-odfdo-notodf>'
    )


def test_zmix_3():
    zmix = ZMix()
    zmix.z_index = 42
    assert zmix.z_index == 42


def test_sizemix_minimal():
    size = SizeMix()
    assert size._canonicalize() == (
        "<draw:sizemix-odfdo-notodf></draw:sizemix-odfdo-notodf>"
    )


def test_sizemix_size_1():
    size = SizeMix()
    size.size = ("10cm", "15cm")
    assert size._canonicalize() == (
        "<draw:sizemix-odfdo-notodf "
        'svg:height="15cm" '
        'svg:width="10cm">'
        "</draw:sizemix-odfdo-notodf>"
    )


def test_sizemix_size_2():
    size = SizeMix()
    size.size = ("10cm", "15cm")
    assert size.size[0] == "10cm"


def test_sizemix_size_3():
    size = SizeMix()
    size.size = ("10cm", "15cm")
    assert size.width == "10cm"


def test_sizemix_size_4():
    size = SizeMix()
    size.size = ("10cm", "15cm")
    assert size.height == "15cm"


def test_sizemix_size_5():
    size = SizeMix()
    size.width = "10cm"
    assert size.size == ("10cm", None)


def test_sizemix_size_6():
    size = SizeMix()
    size.width = "10cm"
    size.height = "15cm"
    assert size.size == ("10cm", "15cm")
