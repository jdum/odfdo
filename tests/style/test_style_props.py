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
from unittest.mock import patch

import pytest

from odfdo.element import Element
from odfdo.style import Style
from odfdo.style_props import StyleProps


def test_check_area_none():
    style = Style("paragraph", name="S1")
    assert style._check_area(None) == "paragraph"


def test_get_properties_invalid_area():
    style = Style("paragraph", name="S1")
    assert style.get_properties(area="invalid_area") is None


def test_get_properties_with_children():
    style = Style("paragraph", name="S1")
    props = Element.from_tag("style:paragraph-properties")
    style.append(props)
    # Use hex for color
    props.set_attribute("fo:color", "#0000FF")
    child = Element.from_tag("style:background-image")
    child.set_attribute("fo:position", "center")
    props.append(child)

    res = style.get_properties()
    assert res["fo:color"] == "#0000FF"
    assert isinstance(res["style:background-image"], dict)
    assert res["style:background-image"]["fo:position"] == "center"


def test_update_boolean_styles_none_values():
    props = {
        "style:text-line-through-style": "none",
        "style:text-underline-style": "none",
    }
    StyleProps._update_boolean_styles(props)
    assert props["strike"] is False
    assert props["underline"] is False


def test_get_list_style_properties():
    style = Style("paragraph", name="S1")
    res = style.get_list_style_properties()
    assert isinstance(res, dict)


def test_apply_valid_properties_no_allowed():
    props_element = Element.from_tag("style:unknown-properties")
    # use valid prefix fo
    properties = {"fo:color": "#0000FF", "invalid": 123}
    StyleProps._apply_valid_properties(
        props_element,
        "unknown_area",
        properties,
    )
    assert props_element.get_attribute("fo:color") == "#0000FF"
    assert props_element.get_attribute("invalid") is None


def test_apply_valid_properties_warn():
    props_element = Element.from_tag("style:text-properties")
    properties = {"svg:color": "#0000FF"}  # not allowed in text area
    with pytest.warns(UserWarning, match="not allowed"):
        StyleProps._apply_valid_properties(
            props_element,
            "text",
            properties,
        )


def test_apply_valid_properties_lo_extensions_off():
    with patch("odfdo.style_props.USE_LO_EXTENSIONS", False):
        props_element = Element.from_tag("style:text-properties")
        properties = {"loext:test": "value"}
        with pytest.warns(UserWarning):
            StyleProps._apply_valid_properties(
                props_element,
                "text",
                properties,
            )
        assert props_element.get_attribute("loext:test") is None


def test_set_properties_style_no_props():
    style1 = Style("paragraph", name="S1")
    style2 = Style("paragraph", name="S2")
    style1.set_properties(style=style2, area="text")
    assert style1.get_element("style:text-properties") is not None


def test_set_properties_style_with_props():
    style1 = Style("paragraph", name="S1")
    style2 = Style("paragraph", name="S2")
    style2.set_properties(color="blue", area="text")
    style1.set_properties(style=style2, area="text")
    assert style1.get_properties(area="text")["fo:color"] == "#0000FF"


def test_set_properties_none_value():
    style = Style("paragraph", name="S1")
    # fo:color is allowed in "text" area
    style.set_properties(color="blue", area="text")
    assert style.get_properties(area="text")["fo:color"] == "#0000FF"
    style.set_properties(color=None, area="text")
    assert "fo:color" not in style.get_properties(area="text")


def test_set_properties_no_args():
    style = Style("paragraph", name="S1")
    style.set_properties()
    assert style.get_element("style:paragraph-properties") is not None


def test_del_properties_no_element():
    style = Style("paragraph", name="S1")
    with pytest.raises(
        ValueError,
        match="The Properties element is non-existent",
    ):
        style.del_properties(properties=["fo:color"])


def test_del_properties_properties_none():
    style = Style("paragraph", name="S1")
    style.set_properties(color="blue", area="text")
    # Should not raise anything, but element must exist
    style.del_properties(properties=None, area="text")
    assert "fo:color" in style.get_properties(area="text")


def test_del_properties_variants():
    style = Style("paragraph", name="S1")
    style.set_properties(color="blue", area="text")
    style.del_properties(properties=["color"], area="text")
    assert "fo:color" not in style.get_properties(area="text")

    style.set_properties(color="blue", area="text")
    style.del_properties(properties=["nonexistent"], area="text")
    assert style.get_properties(area="text")["fo:color"] == "#0000FF"


def test_set_properties_with_properties_and_style():
    style1 = Style("paragraph", name="S1")
    style2 = Style("paragraph", name="S2")
    style2.set_properties(color="red", area="text")
    style1.set_properties(
        properties={"color": "blue"},
        style=style2,
        area="text",
    )
    assert style1.get_properties(area="text")["fo:color"] == "#0000FF"
