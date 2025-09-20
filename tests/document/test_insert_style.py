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

from odfdo.document import Document
from odfdo.element import Element


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
