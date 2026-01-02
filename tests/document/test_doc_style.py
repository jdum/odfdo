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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from importlib import resources as rso

from odfdo.const import ODF_CONTENT, ODF_EXTENSIONS, ODF_MANIFEST, ODF_META, ODF_STYLES
from odfdo.content import Content
from odfdo.document import Document
from odfdo.element import Element
from odfdo.manifest import Manifest
from odfdo.meta import Meta
from odfdo.styles import Styles


def _copied_template(tmp_path, template):
    src = rso.files("odfdo.templates") / template
    dest = tmp_path / template
    dest.write_bytes(src.read_bytes())
    return dest


def test_case_get_styles(samples):
    document = Document(samples("example.odt"))
    styles = document.get_part(ODF_STYLES)
    assert isinstance(styles, Styles)


def test_get_styles(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles()
    assert len(styles) == 83


def test_get_styles_family_paragraph(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="paragraph")
    assert len(styles) == 40


def test_get_styles_family_paragraph_bytes(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family=b"paragraph")
    assert len(styles) == 40


def test_get_styles_family_text(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="text")
    assert len(styles) == 4


def test_get_styles_family_graphic(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="graphic")
    assert len(styles) == 1


def test_get_styles_family_page_layout_automatic(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="page-layout", automatic=True)
    assert len(styles) == 2


def test_get_styles_family_page_layout_no_automatic(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="page-layout")
    assert len(styles) == 2


def test_get_styles_family_master_page(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    styles = document.get_styles(family="master-page")
    assert len(styles) == 2


def test_get_style_automatic(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    style = document.get_style("paragraph", "P1")
    assert style is not None


def test_get_style_named(tmp_path):
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    style = document.get_style("paragraph", "Heading_20_1")
    assert style is not None


def test_show_styles(tmp_path):
    # XXX hard to unit test
    document = Document(_copied_template(tmp_path, "lpod_styles.odt"))
    all_styles = document.show_styles()
    assert "auto   used:" in all_styles
    assert "common used:" in all_styles
    common_styles = document.show_styles(automatic=False)
    assert "auto   used:" not in common_styles
    assert "common used:" in common_styles
    automatic_styles = document.show_styles(common=False)
    assert "auto   used:" in automatic_styles
    assert "common used:" not in automatic_styles
    no_styles = document.show_styles(automatic=False, common=False)
    assert no_styles == ""


def test_bg_image_get_mimetype(samples):
    document = Document(samples("background.odp"))
    mimetype = document.mimetype
    assert mimetype == ODF_EXTENSIONS["odp"]


def test_bg_image_get_content(samples):
    document = Document(samples("background.odp"))
    content = document.get_part(ODF_CONTENT)
    assert isinstance(content, Content)


def test_bg_image_get_meta(samples):
    document = Document(samples("background.odp"))
    meta = document.get_part(ODF_META)
    assert isinstance(meta, Meta)


def test_bg_image_get_styles(samples):
    document = Document(samples("background.odp"))
    styles = document.get_part(ODF_STYLES)
    assert isinstance(styles, Styles)


def test_bg_image_get_manifest(samples):
    document = Document(samples("background.odp"))
    manifest = document.get_part(ODF_MANIFEST)
    assert isinstance(manifest, Manifest)


def test_bg_image_get_body(samples):
    document = Document(samples("background.odp"))
    body = document.body
    assert body.tag == "office:presentation"


def test_bg_image_get_styles_method(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles()
    assert len(styles) == 112


def test_bg_image_get_styles_family_paragraph(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="paragraph")
    assert len(styles) == 7


def test_bg_image_get_styles_family_paragraph_bytes(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family=b"paragraph")
    assert len(styles) == 7


def test_bg_image_get_styles_family_text(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="text")
    assert len(styles) == 0


def test_bg_image_get_styles_family_graphic(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="graphic")
    assert len(styles) == 44


def test_bg_image_get_styles_family_page_layout_automatic(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="page-layout", automatic=True)
    assert len(styles) == 3


def test_bg_image_get_styles_family_page_layout_no_automatic(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="page-layout")
    assert len(styles) == 3


def test_bg_image_get_styles_family_master_page(samples):
    document = Document(samples("background.odp"))
    styles = document.get_styles(family="master-page")
    assert len(styles) == 1


def test_bg_image_get_style_automatic(samples):
    document = Document(samples("background.odp"))
    style = document.get_style("paragraph", "P1")
    assert style is not None


def test_bg_image_get_style_named(samples):
    document = Document(samples("background.odp"))
    style = document.get_style("", "Paper_20_Crumpled")
    assert style is not None


def test_bg_image_add_bg_image(samples):
    document = Document(samples("background.odp"))
    tag = (
        "<draw:fill-image"
        ' draw:name="background_test"'
        ' xlink:href="Pictures/10000000000004B000000640068E29EE.jpg"'
        ' xlink:type="simple"'
        ' xlink:show="embed"'
        ' xlink:actuate="onLoad"'
        " />"
    )
    elem = Element.from_tag(tag)
    # elem should now be a odfdo.image.DrawFillImage instance
    assert elem.__class__.__name__ == "DrawFillImage"
    part = document.get_part("styles")
    container = part.get_element("office:styles")
    container.append(elem)
    # check style is added:
    style = document.get_style("", "background_test")
    assert style is not None


def test_bg_image_add_bg_image_style(samples):
    document = Document(samples("background.odp"))
    tag = (
        "<draw:fill-image"
        ' draw:name="background_test"'
        ' xlink:href="Pictures/10000000000004B000000640068E29EE.jpg"'
        ' xlink:type="simple"'
        ' xlink:show="embed"'
        ' xlink:actuate="onLoad"'
        " />"
    )
    document.insert_style(tag)
    style = document.get_style("", "background_test")
    assert style is not None


def test_bg_image_add_bg_image_style_twice(samples):
    """Check that prior style of same name is replaced."""
    document = Document(samples("background.odp"))
    tag = (
        "<draw:fill-image"
        ' draw:name="background_test"'
        ' xlink:href="Pictures/10000000000004B000000640068E29EE.jpg"'
        ' xlink:type="simple"'
        ' xlink:show="embed"'
        ' xlink:actuate="onLoad"'
        " />"
    )
    nb_styles = len(document.get_styles(""))
    document.insert_style(tag)
    expected = nb_styles + 1
    result = len(document.get_styles(""))
    assert result == expected
    result = len(document.get_styles(""))
    document.insert_style(tag)
    assert result == expected


def test_bg_image_show_styles(samples):
    document = Document(samples("background.odp"))
    # XXX hard to unit test
    all_styles = document.show_styles()
    assert "auto   used:" in all_styles
    assert "common used:" in all_styles
    common_styles = document.show_styles(automatic=False)
    assert "auto   used:" not in common_styles
    assert "common used:" in common_styles
    automatic_styles = document.show_styles(common=False)
    assert "auto   used:" in automatic_styles
    assert "common used:" not in automatic_styles
    no_styles = document.show_styles(automatic=False, common=False)
    assert no_styles == ""
