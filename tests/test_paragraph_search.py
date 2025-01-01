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

from collections.abc import Iterable

import pytest

from odfdo.paragraph import Paragraph


@pytest.fixture
def paragraph() -> Iterable[Paragraph]:
    txt = (
        "A test,\n   \twith a word and another word\n\n some \xe9 "
        "and \t and  5 spaces, and another word."
    )
    para = Paragraph()
    para.append(txt)
    yield para


def _test_search_word(paragraph):
    expected = (
        '<text:p>A test,<text:line-break/> <text:s text:c="2"/>'
        "<text:tab/>with a word and another word<text:line-break/>"
        "<text:line-break/> some é and <text:tab/> and <text:s/>"
        "5 spaces, and another word.</text:p>"
    )
    print(paragraph.serialize())
    assert paragraph.serialize() == expected


def test_search_test(paragraph):
    result = paragraph.search("test")
    print(result)
    assert result == 2


def test_search_none(paragraph):
    result = paragraph.search("bad")
    print(result)
    assert result is None


def test_search_word_1(paragraph):
    result = paragraph.search("word")
    assert result == 19


def test_search_search_first_test(paragraph):
    result = paragraph.search_first("test")
    print(result)
    assert result == (2, 6)


def test_search_first_none(paragraph):
    result = paragraph.search_first("bad")
    print(result)
    assert result is None


def test_search_first_word(paragraph):
    result = paragraph.search_first("word")
    print(result)
    assert result == (19, 23)


def test_text_at_test(paragraph):
    result1 = paragraph.search_first("test")
    result = paragraph.text_at(result1[0], result1[1])
    assert result == "test"


def test_text_at_none(paragraph):
    result = paragraph.text_at(-1, -1)
    assert result == ""


def test_text_at_all_1(paragraph):
    result = paragraph.text_at(-1)
    assert result == paragraph.inner_text


def test_text_at_all_2(paragraph):
    result = paragraph.text_at(0)
    assert result == paragraph.inner_text


def test_text_at_all_3(paragraph):
    result = paragraph.text_at(1)
    assert result == paragraph.inner_text[1:]


def test_text_at_word(paragraph):
    result1 = paragraph.search_first("word")
    result = paragraph.text_at(result1[0], result1[1])
    assert result == "word"


def test_search_test_regex(paragraph):
    result = paragraph.search(r"t..t")
    print(result)
    assert result == 2


def test_search_no_number_regex(paragraph):
    result = paragraph.search(r"[0-4]+")
    print(result)
    assert result is None


def test_search_word_1_regex(paragraph):
    result = paragraph.search(r"w[word]+")
    print(result)
    assert result == 19


def test_search_search_all_test(paragraph):
    result = paragraph.search_all("test")
    print(result)
    assert result == [(2, 6)]


def test_search_search_all_word(paragraph):
    result = paragraph.search_all("word")
    print(result)
    assert result == [(19, 23), (36, 40), (83, 87)]


def test_search_search_all_word_text_at(paragraph):
    result1 = paragraph.search_all("word")
    result = [paragraph.text_at(p[0], p[1]) for p in result1]
    assert result == ["word", "word", "word"]


def test_search_search_all_word_text_at_no_end(paragraph):
    result1 = paragraph.search_all("word")
    result = [paragraph.text_at(p[0], p[1]) for p in result1]
    assert result == ["word", "word", "word"]


def test_search_search_all_regex(paragraph):
    result = paragraph.search_all(r"a\w+")
    print(result)
    assert result == [
        (24, 27),
        (28, 35),
        (50, 53),
        (56, 59),
        (65, 69),
        (71, 74),
        (75, 82),
    ]


def test_search_search_all_regex_text_at(paragraph):
    result1 = paragraph.search_all(r"a\w+")
    result = [paragraph.text_at(p[0], p[1]) for p in result1]
    print(result)
    assert result == ["and", "another", "and", "and", "aces", "and", "another"]
