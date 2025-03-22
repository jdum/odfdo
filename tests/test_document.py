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
#          Luis Belmar-Letelier <luis@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from importlib import resources as rso
from io import BytesIO

import pytest

from odfdo.const import ODF_CONTENT, ODF_EXTENSIONS, ODF_MANIFEST, ODF_META, ODF_STYLES
from odfdo.content import Content
from odfdo.document import Document
from odfdo.element import Element
from odfdo.manifest import Manifest
from odfdo.meta import Meta
from odfdo.paragraph import Paragraph
from odfdo.styles import Styles


def _copied_template(tmp_path, template):
    src = rso.files("odfdo.templates") / template
    dest = tmp_path / template
    dest.write_bytes(src.read_bytes())
    return dest


def test_non_existing(samples):
    with pytest.raises(IOError):
        Document(samples("notexisting"))


def test_text_template(tmp_path):
    template = _copied_template(tmp_path, "text.ott")
    print(template)
    assert Document.new(template)


def test_spreadsheet_template(tmp_path):
    template = _copied_template(tmp_path, "spreadsheet.ots")
    assert Document.new(template)


def test_presentation_template(tmp_path):
    template = _copied_template(tmp_path, "presentation.otp")
    assert Document.new(template)


def test_drawing_template(tmp_path):
    template = _copied_template(tmp_path, "drawing.otg")
    assert Document.new(template)


def test_mimetype(tmp_path):
    template = _copied_template(tmp_path, "drawing.otg")
    document = Document.new(template)
    mimetype = document.mimetype
    assert "template" not in mimetype
    manifest = document.get_part(ODF_MANIFEST)
    media_type = manifest.get_media_type("/")
    assert "template" not in media_type


def test_bad_type():
    with pytest.raises(IOError):
        Document.new("foobar")


def test_text_type():
    document = Document("text")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_text_type_2():
    document = Document("texte")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_text_type_3():
    document = Document("odt")
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_spreadsheet_type():
    document = Document.new("spreadsheet")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_spreadsheet_type_2():
    document = Document.new("tableur")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_spreadsheet_type_3():
    document = Document.new("ods")
    assert document.mimetype == ODF_EXTENSIONS["ods"]


def test_presentation_type():
    document = Document("presentation")
    assert document.mimetype == ODF_EXTENSIONS["odp"]


def test_presentation_type_2():
    document = Document("odp")
    assert document.mimetype == ODF_EXTENSIONS["odp"]


def test_drawing_type():
    document = Document.new("drawing")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_2():
    document = Document.new("odg")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_3():
    document = Document.new("graphics")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_drawing_type_4():
    document = Document.new("graphic")
    assert document.mimetype == ODF_EXTENSIONS["odg"]


def test_case_filesystem(samples):
    assert Document(samples("example.odt"))


def test_case_get_mimetype(samples):
    document = Document(samples("example.odt"))
    assert document.mimetype == ODF_EXTENSIONS["odt"]


def test_case_get_content(samples):
    document = Document(samples("example.odt"))
    content = document.get_part(ODF_CONTENT)
    assert isinstance(content, Content)


def test_case_get_meta(samples):
    document = Document(samples("example.odt"))
    meta = document.get_part(ODF_META)
    assert isinstance(meta, Meta)


def test_case_get_styles(samples):
    document = Document(samples("example.odt"))
    styles = document.get_part(ODF_STYLES)
    assert isinstance(styles, Styles)


def test_case_get_manifest(samples):
    document = Document(samples("example.odt"))
    manifest = document.get_part(ODF_MANIFEST)
    assert isinstance(manifest, Manifest)


def test_case_get_body(samples):
    document = Document(samples("example.odt"))
    body = document.body
    assert body.tag == "office:text"


def test_case_clone_body_none(samples):
    document = Document(samples("example.odt"))
    _dummy = document.body
    clone = document.clone
    # new body cache should be empty
    assert clone._Document__body is None


def test_case_clone_xmlparts_empty(samples):
    document = Document(samples("example.odt"))
    clone = document.clone
    # new xmlparts cache should be empty
    assert clone._Document__xmlparts == {}


def test_case_clone_same_content(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    s_clone = clone.body.serialize()
    assert s_clone == s_orig


def test_case_clone_different_changes_1(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_clone = clone.body.serialize()
    assert s_clone != s_orig


def test_case_clone_different_unchanged_1(samples):
    document = Document(samples("example.odt"))
    s_orig = document.body.serialize()
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_after = document.body.serialize()
    assert s_after == s_orig


def test_case_clone_different_unchanged_2(samples):
    document = Document(samples("example.odt"))
    clone = document.clone
    clone.body.append(Paragraph("some text"))
    s_clone1 = clone.body.serialize()
    document.body.append(Paragraph("new text"))
    s_clone2 = clone.body.serialize()
    assert s_clone1 == s_clone2


def test_case_save_nogenerator(tmp_path, samples):
    document = Document(samples("example.odt"))
    temp = BytesIO()
    document.save(temp)
    temp.seek(0)
    new = Document(temp)
    generator = new.get_part(ODF_META).get_generator()
    assert generator.startswith("odfdo")


def test_case_save_generator(samples):
    document = Document(samples("example.odt"))
    document.get_part(ODF_META).set_generator("toto")
    temp = BytesIO()
    document.save(temp)
    temp.seek(0)
    new = Document(temp)
    generator = new.get_part(ODF_META).get_generator()
    assert generator == "toto"


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


def test_repr_empty():
    document = Document()
    assert repr(document) == "<Document type=text path=None>"


def test_repr_text(samples):
    document = Document(samples("example.odt"))
    assert "example.odt" in repr(document)


def test_repr_spreadsheet(samples):
    document = Document(samples("simple_table.ods"))
    result = repr(document)
    assert "type=spreadsheet" in result
    assert "simple_table.ods" in result


def test_str_empty():
    document = Document()
    document.body.clear()
    assert str(document) == ""


def test_str_text(samples):
    document = Document(samples("example.odt"))
    result = str(document)
    assert "odfdo Test Case Document" in result
    assert "This is the second paragraph" in result
    assert "First paragraph[*] of the second section" in result


def test_str_spreadsheet(samples):
    document = Document(samples("simple_table.ods"))
    result = str(document)
    assert "1 1 1 2 3 3 3" in result
    assert "A float" in result
    assert "3.14" in result


def test_insert_style_paragraph(samples):
    document = Document(samples("example.odt"))
    style = Element.from_tag(
        '<style:style style:name="custom" '
        'style:display-name="custom" '
        'style:family="paragraph" '
        'style:parent-style-name="Text">'
        '<style:paragraph-properties fo:margin-left="2cm"/>'
        '<style:text-properties fo:color="#808080" loext:opacity="100%" '
        'fo:font-size="16pt" fo:font-style="normal" '
        'style:text-underline-style="solid" '
        'style:text-underline-width="auto" '
        'style:text-underline-color="font-color" '
        'fo:font-weight="bold"/>'
        "</style:style>"
    )
    nb_styles = len(document.get_styles("paragraph"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("paragraph"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("paragraph"))
    assert result == expected


def test_insert_style_date(samples):
    document = Document(samples("example.odt"))
    style = Element.from_tag(
        "<number:date-style "
        'style:name="nr-nl-date" '
        'number:automatic-order="true">'
        '<number:day number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:month number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:year number:style="long"/>'
        "</number:date-style>"
    )
    nb_styles = len(document.get_styles("date"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("date"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("date"))
    assert result == expected
    result2 = document.get_style("date", "nr-nl-date")
    assert result2


def test_insert_style_currency(samples):
    document = Document(samples("example.odt"))
    style = Element.from_tag(
        "<number:currency-style "
        'style:name="nr-nl-currency-gt0" '
        'style:volatile="true">'
        "<number:currency-symbol "
        'number:language="nl" '
        'number:country="NL">€</number:currency-symbol>'
        "<number:text> </number:text>"
        '<number:number number:decimal-places="2"'
        ' number:min-decimal-places="2" '
        'number:min-integer-digits="1"/>'
        "</number:currency-style>"
    )
    nb_styles = len(document.get_styles("currency"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("currency"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("currency"))
    assert result == expected
    result2 = document.get_style("currency", "nr-nl-currency-gt0")
    assert result2


def test_insert_style_currency_2(samples):
    document = Document(samples("example.odt"))
    style = Element.from_tag(
        "<number:currency-style "
        'style:name="nr-nl-currency">'
        "<number:currency-symbol "
        'number:language="nl" '
        'number:country="NL">€</number:currency-symbol>'
        "<number:text> </number:text>"
        '<number:number number:decimal-places="2" '
        'number:min-decimal-places="2" '
        'number:min-integer-digits="1"/>'
        "<number:text>-</number:text>"
        "<style:map "
        'style:condition="value()&gt;=0" '
        'style:apply-style-name="nr-nl-currency-gt0"/>'
        "</number:currency-style>"
    )
    nb_styles = len(document.get_styles("currency"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("currency"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("currency"))
    assert result == expected
    result2 = document.get_style("currency", "nr-nl-currency")
    assert result2


def test_insert_style_composite_1(samples):
    document = Document(samples("example.odt"))
    style_date = Element.from_tag(
        "<number:date-style "
        'style:name="nr-nl-date" '
        'number:automatic-order="true">'
        '<number:day number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:month number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:year number:style="long"/>'
        "</number:date-style>"
    )
    document.insert_style(style_date)
    style_cur = Element.from_tag(
        "<number:currency-style "
        'style:name="nr-nl-currency">'
        "<number:currency-symbol "
        'number:language="nl" '
        'number:country="NL">€</number:currency-symbol>'
        "<number:text> </number:text>"
        '<number:number number:decimal-places="2" '
        'number:min-decimal-places="2" '
        'number:min-integer-digits="1"/>'
        "<number:text>-</number:text>"
        "<style:map "
        'style:condition="value()&gt;=0" '
        'style:apply-style-name="nr-nl-currency-gt0"/>'
        "</number:currency-style>"
    )
    document.insert_style(style_cur)
    style = Element.from_tag(
        "<style:style "
        'style:name="nldate" '
        'style:family="table-cell" '
        'style:parent-style-name="Default" '
        'style:data-style-name="nr-nl-date"/>'
    )
    nb_styles = len(document.get_styles("table-cell"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("table-cell"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("table-cell"))
    assert result == expected


def test_insert_style_composite_2(samples):
    document = Document(samples("example.odt"))
    style_date = Element.from_tag(
        "<number:date-style "
        'style:name="nr-nl-date" '
        'number:automatic-order="true">'
        '<number:day number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:month number:style="long"/>'
        "<number:text>-</number:text>"
        '<number:year number:style="long"/>'
        "</number:date-style>"
    )
    document.insert_style(style_date)
    style_cur = Element.from_tag(
        "<number:currency-style "
        'style:name="nr-nl-currency">'
        "<number:currency-symbol "
        'number:language="nl" '
        'number:country="NL">€</number:currency-symbol>'
        "<number:text> </number:text>"
        '<number:number number:decimal-places="2" '
        'number:min-decimal-places="2" '
        'number:min-integer-digits="1"/>'
        "<number:text>-</number:text>"
        "<style:map "
        'style:condition="value()&gt;=0" '
        'style:apply-style-name="nr-nl-currency-gt0"/>'
        "</number:currency-style>"
    )
    document.insert_style(style_cur)
    style = Element.from_tag(
        "<style:style "
        'style:name="nlcurrency" '
        'style:family="table-cell" '
        'style:parent-style-name="Default" '
        'style:data-style-name="nr-nl-currency"/>'
    )
    nb_styles = len(document.get_styles("table-cell"))
    document.insert_style(style)
    expected = nb_styles + 1
    result = len(document.get_styles("table-cell"))
    assert result == expected
    document.insert_style(style)
    result = len(document.get_styles("table-cell"))
    assert result == expected
