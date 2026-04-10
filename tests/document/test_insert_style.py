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
from io import BytesIO
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from odfdo.const import (
    XML,
    ZIP,
)
from odfdo.document import (
    AUTOMATIC_PREFIX,
    Document,
)
from odfdo.element import Element
from odfdo.image import DrawFillImage
from odfdo.page_layout import StylePageLayout
from odfdo.style import Style


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


def test_document_insert_style_errors():
    doc = Document("text")
    with pytest.raises(TypeError, match="Unknown Style type"):
        doc.insert_style(123)

    style = Element.from_tag('<style:style style:family="paragraph"/>')
    with pytest.raises(AttributeError):
        doc.insert_style(style)


def test_document_insert_style_font_face():
    doc = Document("text")
    style = Style("font-face", font_name="MyFont")
    doc.insert_style(style)
    doc.insert_style(style, default=True)


def test_document_insert_style_page_layout():
    doc = Document("text")
    style = StylePageLayout("MyLayout")
    doc.insert_style(style)


def test_document_insert_style_draw_fill_image():
    doc = Document("text")
    style = DrawFillImage(name="MyImg")
    doc.insert_style(style)


def test_insert_style_automatic_no_name_provided():
    doc = Document("text")
    style = Style("paragraph")
    # Coverage for else branch: self._set_automatic_name
    name = doc.insert_style(style, automatic=True)
    assert name.startswith(AUTOMATIC_PREFIX)


def test_merge_styles_from_stylename_none_branch():
    doc1 = Document("text")
    doc2 = Document("text")
    # Style without name but with family
    style = Element.from_tag("style:style")
    style.set_attribute("style:family", "paragraph")
    # Manually append to common styles of doc1
    doc1.styles.get_element("//office:styles").append(style)
    # stylename will be None
    doc2.merge_styles_from(doc1)
    # Should find it via family and None name
    assert doc2.styles.get_style("paragraph", None) is not None


def test_merge_styles_from_invalid_container():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    # Put it in a wrong container name
    wrong_container = Element.from_tag("office:wrong")
    styles_part = Element.from_tag("office:document-styles")
    styles_part.append(wrong_container)
    wrong_container.append(style)

    with patch.object(Document, "get_styles", return_value=[style]):
        with pytest.raises(NotImplementedError):
            doc2.merge_styles_from(doc1)


def test_clone_no_container_branch():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.clone


def test_save_pretty_no_packaging_xml():
    doc = Document("text")
    out = BytesIO()
    # packaging is ZIP, pretty is True
    doc.save(target=out, pretty=True)
    assert out.getvalue() != b""


def test_save_not_pretty_xml_packaging():
    doc = Document("text")
    out = BytesIO()
    # packaging is XML, pretty is False
    doc.save(target=out, packaging=XML, pretty=False)
    assert out.getvalue() != b""


def test_insert_style_automatic_name_exists():
    doc = Document("text")
    style = Style("paragraph", name="P1")
    # Coverage for if name: in _insert_style_get_automatic_styles
    # and if hasattr(style, "name"):
    doc.insert_style(style, name="P2", automatic=True)
    assert style.name == "P2"


def test_merge_styles_from_no_family():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Element.from_tag("style:style")
    # family is None
    doc1.styles.get_element("//office:styles").append(style)
    doc2.merge_styles_from(doc1)
    # Should skip it


def test_merge_styles_from_no_container():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    # style has no parent
    with patch.object(Document, "get_styles", return_value=[style]):
        doc2.merge_styles_from(doc1)
        # Should skip it


def test_merge_styles_from_no_upper_container():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    container = Element.from_tag("office:styles")
    # Put it in a wrong parent
    wrong = Element.from_tag("office:wrong")
    wrong.append(container)
    container.append(style)
    # style.parent is container, container.parent is wrong
    with patch.object(Document, "get_styles", return_value=[style]):
        with pytest.raises(NotImplementedError):
            doc2.merge_styles_from(doc1)


def test_get_formatted_text_footnotes_non_rst_branch():
    doc = Document("text")
    result = []
    context = {
        "footnotes": [("1", "body")],
        "annotations": [],
        "images": [],
        "endnotes": [],
    }
    doc._get_formatted_text_footnotes(result, context, rst_mode=False)
    assert "----\n" in "".join(result)
    assert "[1] body\n" in "".join(result)


def test_add_binary_part_no_container():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        doc._add_binary_part(MagicMock())


def test_clone_no_container():
    doc = Document()
    doc.container = None
    with pytest.raises(ValueError, match="Empty Container"):
        _ = doc.clone


def test_save_target_none_zip():
    doc = Document("text")
    doc.container.path = None
    with pytest.raises(
        ValueError, match="Saving a document without path requires a target"
    ):
        doc.save(target=None, packaging=ZIP)


def test_save_target_none_general():
    doc = Document("text")
    doc.container.path = None
    with pytest.raises(
        ValueError, match="Saving a document without path requires a target"
    ):
        doc.save(target=None, packaging="folder")


def test_save_backup_str():
    doc = Document("text")
    doc.container = MagicMock()
    # Mocking basic behavior for save() to reach backup check
    doc.container.get_part.return_value = b'<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" office:version="1.2"><office:meta><meta:generator>ODFDO</meta:generator></office:meta></office:document-meta>'
    doc.save(target="some_path.odt", backup=True)
    doc.container.save.assert_called()


def test_insert_style_automatic_name_branch():
    doc = Document("text")
    style = Style("paragraph", name="P1")
    doc.insert_style(style, name="NEW_NAME", automatic=True)
    assert style.name == "NEW_NAME"


def test_insert_style_automatic_hasattr_name_false():
    doc = Document("text")
    style = Element.from_tag("style:style")
    style.set_attribute("style:family", "paragraph")
    doc.insert_style(style, name="ANY", automatic=True)


def test_insert_style_draw_fill_image_old():
    doc = Document("text")
    fill_image = DrawFillImage("test_image", "Pictures/test.png")
    name = doc.insert_style(fill_image)
    assert name == "test_image"


def test_insert_style_invalid_family():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    style.family = "invalid_family"
    with pytest.raises(ValueError, match="Invalid style"):
        doc.insert_style(style)


def test_insert_style_default_no_name_old():
    doc = Document("text")
    style = Style("paragraph")
    doc.insert_style(style, default=True)
    assert style.tag == "style:default-style"


def test_insert_style_combinations_old_old():
    doc = Document("text")
    style = Style("paragraph", name="MyStyle")
    with pytest.raises(AttributeError, match="Invalid combination of arguments"):
        doc.insert_style(style, automatic=True, default=True)


def test_unique_style_name_old_old():
    doc = Document("text")
    name = doc._unique_style_name("ta")
    assert name == "ta_0"
    doc.insert_style(Style("paragraph", name="ta_0"))
    name2 = doc._unique_style_name("ta")
    assert name2 == "ta_1"


def test_show_styles_draw_fill_image_old_old():
    doc = Document("text")
    fill_image = DrawFillImage("test_fill", "Pictures/test.png")
    doc.insert_style(fill_image)
    res = doc.show_styles()
    assert "test_fill" in res


def test_insert_style_automatic_with_name_old_old():
    doc = Document("text")
    style = Style("paragraph", name="P_AUTO")
    name = doc.insert_style(style, name="P_AUTO_NEW", automatic=True)
    assert name == "P_AUTO_NEW"
    assert style.name == "P_AUTO_NEW"


def test_insert_style_default_with_name_old_old():
    doc = Document("text")
    style = Style("paragraph", name="P_DEFAULT")
    doc.insert_style(style, name="IGNORED", default=True)
    assert style.tag == "style:default-style"
    assert style.get_attribute("style:name") is None


def test_insert_style_string_xml_old_old():
    doc = Document("text")
    style_xml = '<style:style style:name="P_XML" style:family="paragraph"/>'
    name = doc.insert_style(style_xml)
    assert name == "P_XML"


def test_insert_style_hasattr_name_false_branch():
    doc = Document("text")
    # Use a real Element but hide its 'name' attribute
    style = Element.from_tag("style:style")
    style.set_attribute("style:family", "paragraph")

    with patch.object(style.__class__, "name", new_callable=PropertyMock) as mock_name:
        mock_name.side_effect = AttributeError
        # Now hasattr(style, "name") is False, so style.name = name is skipped
        doc.insert_style(style, name="NEW_NAME", automatic=True)

    # Verify it was NOT set
    assert style.get_attribute("style:name") is None


def test_merge_styles_from_no_dest():
    doc1 = Document("text")
    doc2 = Document("text")
    style = Style("paragraph", name="P1")
    doc1.styles.get_element("//office:styles").append(style)
    # Mock doc2 parts directly
    doc2.styles.get_element = MagicMock(return_value=None)
    doc2.content.get_element = MagicMock(return_value=None)
    doc2.merge_styles_from(doc1)


def test_add_page_break_style_branches():
    doc = Document("text")
    # 1. False branch: exists but NOT perfect
    style = Style("paragraph", name="odfdopagebreak")
    # No break property
    style.set_properties(area="paragraph", text_align="center")
    doc.insert_style(style, automatic=False)
    doc.add_page_break_style()

    # 2. True branch: exists AND perfect
    doc.add_page_break_style()
    assert doc.get_style("paragraph", "odfdopagebreak") is not None


def test_show_styles_attribute_error():
    doc = Document("text")
    style = Style("paragraph", name="P1")
    with patch.object(Style, "name", new_callable=PropertyMock) as mock_name:
        mock_name.side_effect = AttributeError
        with patch.object(Document, "get_styles", return_value=[style]):
            with pytest.raises(AttributeError):
                doc.show_styles()
