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
# Authors: Hervé Cauwelier <herve@itaapy.com>

from collections.abc import Iterable
from typing import cast
from unittest.mock import patch

import pytest

from odfdo.const import ODF_CONTENT, ODF_STYLES
from odfdo.content import Content
from odfdo.document import Document
from odfdo.element import Element
from odfdo.style import (
    Style,
    _make_line_string,
    _make_thick_string,
    make_table_cell_border_string,
)


@pytest.fixture
def content(samples) -> Iterable[Content]:
    document = Document(samples("span_style.odt"))
    content = cast(Content, document.get_part(ODF_CONTENT))
    yield content


def test_get_styles(content):
    styles = content.get_styles()
    assert len(styles) == 7


def test_get_styles_family(content):
    styles = content.get_styles(family="paragraph")
    assert len(styles) == 2


def test_get_style_automatic(content):
    style = content.get_style("paragraph", "P1")
    assert style is not None


def test_insert_style(content):
    style = Style(
        "paragraph",
        "style1",
        area="text",
        **{"fo:color": "#0000ff", "fo:background-color": "#ff0000"},
    )
    auto_styles = content.get_element("//office:automatic-styles")
    auto_styles.append(style)
    read_style = content.get_style("paragraph", "style1")

    expected = (
        "<style:style "
        'style:family="paragraph" style:name="style1">'
        "<style:text-properties "
        'fo:background-color="#ff0000" fo:color="#0000ff">'
        "</style:text-properties>"
        "</style:style>"
    )
    assert read_style._canonicalize() == expected


def test_get_styles_none(content):
    styles = content.get_styles(family=None)
    assert len(styles) == 7


def test_get_styles_nonexistent(content):
    with pytest.raises(ValueError, match="Unknown family"):
        content.get_styles(family="nonexistent")


def test_get_style_not_found(content):
    style = content.get_style("paragraph", "nonexistent")
    assert style is None


def test_get_style_by_element(content):
    style = content.get_style("paragraph", "P1")
    read_style = content.get_style("paragraph", style)
    assert read_style == style


def test_get_style_by_element_error(content):
    element = Element.from_tag("<text:p/>")
    with pytest.raises(ValueError, match="Not a odf_style"):
        content.get_style("paragraph", element)


def test_get_style_by_display_name(content):
    style = content.get_style("paragraph", "P1")
    style.set_attribute("style:display-name", "My Display Name")
    read_style = content.get_style(
        "paragraph",
        display_name="My Display Name",
    )
    assert read_style._canonicalize() == style._canonicalize()


def test_get_style_no_family(content):
    # get font face by name (it has style:name but no style:family)
    style = content.get_style("", "Liberation Serif")
    assert style.tag == "style:font-face"


def test_get_style_no_family_draw_name():
    # Test matching draw:name when family is empty
    container = Element.from_tag("<office:styles/>")
    # draw:fill-image uses draw:name
    tag = '<draw:fill-image draw:name="img1" xlink:href="url1" />'
    img = Element.from_tag(tag)
    container.append(img)

    style = container.get_style("", "img1")
    assert style.tag == "draw:fill-image"
    assert style.get_attribute("draw:name") == "img1"


def test_get_style_no_family_display_name():
    # Test matching display-name when family is empty
    container = Element.from_tag("<office:styles/>")
    tag = '<style:style style:name="s1" style:display-name="Display 1" />'
    s = Element.from_tag(tag)
    container.append(s)

    style = container.get_style("", display_name="Display 1")
    assert style.get_attribute("style:name") == "s1"


def test_get_style_no_family_first():
    # Test getting first style when family and names are empty
    container = Element.from_tag("<office:styles/>")
    tag1 = '<style:style style:name="s1" />'
    tag2 = '<style:style style:name="s2" />'
    container.append(Element.from_tag(tag1))
    container.append(Element.from_tag(tag2))

    style = container.get_style("")
    assert style.get_attribute("style:name") == "s1"


def test_get_style_default_by_family(samples):
    document = Document(samples("example.odt"))
    styles_part = document.get_part(ODF_STYLES)
    # Testing get_style(family, name=None) which should return default style
    style = styles_part.get_style("paragraph")
    assert style.tag == "style:default-style"
    assert style.get_attribute("style:family") == "paragraph"


def test_get_styles_all_no_family(samples):
    document = Document(samples("example.odt"))
    styles_part = document.get_part(ODF_STYLES)
    styles = styles_part.get_styles()  # family="" by default
    assert len(styles) > 0
    # Should include default styles, markers, fill-images etc.
    tags = {s.tag for s in styles}
    assert "style:default-style" in tags


def test_make_thick_string_variants():
    assert _make_thick_string(None) == "0.06pt"
    assert _make_thick_string("") == "0.06pt"
    assert _make_thick_string("  1pt  ") == "1pt"
    assert _make_thick_string(0.5) == "0.50pt"
    assert _make_thick_string(100) == "1.00pt"
    with pytest.raises(ValueError, match="Thickness must be None"):
        _make_thick_string([])


def test_make_line_string_variants():
    assert _make_line_string(None) == "solid"
    assert _make_line_string("") == "solid"
    assert _make_line_string("  dotted  ") == "dotted"
    with pytest.raises(ValueError, match="Line style must be None"):
        _make_line_string([])


def test_make_table_cell_border_string():
    res = make_table_cell_border_string(
        thick=1.0,
        line="dashed",
        color="blue",
    )
    assert res == "1.00pt dashed #0000FF"


def test_style_init_errors():
    obj = object.__new__(Style)
    with pytest.raises(TypeError, match="Wrong initializer"):
        obj.__init__(family="master-page")
    with pytest.raises(ValueError, match="Unknown family"):
        obj.__init__(family="unknown")


def test_style_init_font_face_error():
    obj = object.__new__(Style)
    with pytest.raises(ValueError, match="font_name is required"):
        obj.__init__(family="font-face")


def test_style_init_table_align_error():
    with pytest.raises(ValueError, match="Invalid align value"):
        Style(family="table", align="invalid")


def test_style_family_setter():
    style = Style(family="paragraph")
    style.family = "text"
    assert style.get_attribute("style:family") == "text"


def test_style_family_none_lazy():
    elem = Element.from_tag("text:list-style")
    style = Style(tag_or_elem=elem._Element__element)
    assert style.family == "list"


def test_style_get_level_style_non_list():
    style = Style(family="paragraph")
    assert style.get_level_style(1) is None


def test_style_set_level_style_non_list():
    style = Style(family="paragraph")
    assert style.set_level_style(1, num_format="1") is None


def test_style_set_level_style_unknown_type():
    style = Style(family="list")
    with pytest.raises(ValueError, match="unknown level style type"):
        style.set_level_style(1)


def test_style_set_level_style_existing_transmute():
    style = Style(family="list")
    style.set_level_style(1, bullet_char="*")
    style.set_level_style(1, num_format="1")
    level1 = style.get_level_style(1)
    assert level1.tag == "text:list-level-style-number"


def test_style_set_level_style_other_args():
    style = Style(family="list")
    style.set_level_style(
        1,
        num_format="1",
        display_levels=2,
        start_value=5,
        style="T1",
    )
    level1 = style.get_level_style(1)
    assert level1.get_attribute("text:display-levels") == "2"
    assert level1.get_attribute("text:start-value") == "5"
    assert level1.text_style == "T1"


def test_style_set_level_style_none_return():
    style = Style(family="list")
    with patch.object(Element, "from_tag", return_value=None):
        assert style.set_level_style(1, num_format="1") is None


def test_set_font_full():
    style = Style(
        family="font-face",
        font_name="Arial",
        font_family_generic="swiss",
    )
    assert style.font_family_generic == "swiss"

    style.set_font("Courier", family_generic="roman")
    assert style.font_family_generic == "roman"

    style.set_font("Verdana", family=None)
    assert style.svg_font_family == '"Verdana"'


def test_set_font_non_font_face():
    style = Style(family="paragraph")
    style.set_font("Arial")
    assert style.name is None


def test_style_repr():
    style = Style(family="paragraph", name="S1")
    assert "family=paragraph" in repr(style)
    assert "name=S1" in repr(style)


def test_style_init_various_families_missing_branches_1():
    s1 = Style("paragraph", area="text")
    props = s1.get_properties(area="text")
    assert props is None


def test_style_init_various_families_missing_branches_2():
    s2 = Style("paragraph", area="table-cell")
    props2 = s2.get_properties(area="table-cell")
    assert props2 is None


def test_style_init_various_families_missing_branches_3():
    s3 = Style("paragraph", area="table-row")
    assert s3.get_properties(area="table-row") is None


def test_style_init_various_families_missing_branches_4():
    s4 = Style("paragraph", area="table-column")
    assert s4.get_properties(area="table-column") is None


def test_style_init_various_families_missing_branches_5():
    s5 = Style("paragraph", area="table")
    assert s5.get_properties(area="table") is None


def test_style_init_various_families_missing_branches_6():
    s6 = Style("paragraph", area="graphic")
    assert s6.get_properties(area="graphic") is None


def test_style_init_various_families():
    s = Style(
        "paragraph",
        name="S1",
        display_name="D1",
        parent_style="P1",
        master_page="M1",
    )
    assert s.name == "S1"
    assert s.display_name == "D1"
    assert s.parent_style == "P1"
    assert s.master_page == "M1"


def test_style_init_various_families_1():
    s1 = Style(
        "text",
        italic=True,
        bold=True,
        color="blue",
        background_color="red",
    )
    props = s1.get_properties()
    assert props["fo:font-style"] == "italic"
    assert props["fo:font-weight"] == "bold"


def test_style_init_various_families_2():
    s2 = Style("table-cell", shadow="gray", background_color="yellow")
    props = s2.get_properties()
    assert props["style:shadow"] == "gray"
    assert props["fo:background-color"] == "#FFFF00"


def test_style_init_various_families_3():
    s3 = Style(
        "table-row",
        height="1cm",
        use_optimal_height=True,
        background_color="blue",
    )
    props = s3.get_properties()
    assert props["style:row-height"] == "1cm"
    assert props["style:use-optimal-row-height"] == "true"
    assert props["fo:background-color"] == "#0000FF"


def test_style_init_various_families_4():
    s4 = Style(
        "table-column",
        width="2cm",
        break_before="page",
        break_after="column",
    )
    props = s4.get_properties()
    assert props["style:column-width"] == "2cm"
    assert props["fo:break-before"] == "page"
    assert props["fo:break-after"] == "column"

    s_table = Style("table", width="15cm", align="center")
    props = s_table.get_properties()
    assert props["style:width"] == "15cm"
    assert props["table:align"] == "center"


def test_style_init_various_families_5():
    s5 = Style("graphic", min_height="3cm")
    props = s5.get_properties()
    assert props["fo:min-height"] == "3cm"


def test_style_set_level_style_url_and_clone():
    style = Style("list")
    style.set_level_style(1, url="img.png", prefix="(", suffix=")")
    level1 = style.get_level_style(1)
    assert level1.tag == "text:list-level-style-image"
    assert level1.get_attribute("xlink:href") == "img.png"
    assert level1.get_attribute("style:num-prefix") == "("
    assert level1.get_attribute("style:num-suffix") == ")"

    style2 = Style("list")
    style2.set_level_style(1, clone=level1)
    assert style2.get_level_style(1).get_attribute("xlink:href") == "img.png"


def test_style_init_font_face_full():
    s = Style(
        "font-face",
        font_name="MyFont",
        font_family="Serif",
        font_family_generic="roman",
        font_pitch="fixed",
    )
    assert s.name == "MyFont"
    assert s.svg_font_family == '"Serif"'
    assert s.font_family_generic == "roman"
    assert s.font_pitch == "fixed"
