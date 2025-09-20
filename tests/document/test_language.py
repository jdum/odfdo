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


import pytest

from odfdo.document import Document


def test_read_lang(samples):
    doc = Document(samples("example.odt"))
    assert doc.language == "fr-FR"


def test_set_lang(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en-US"
    assert doc.language == "en-US"


def test_set_lang_meta(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en-US"
    assert doc.meta.language == "en-US"


def test_set_lang_styles(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en-US"
    assert doc.styles.default_language == "en-US"


def test_set_lang_no_country(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en"
    assert doc.language == "en"


def test_set_lang_meta_no_country(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en"
    assert doc.meta.language == "en"


def test_set_lang_styles_no_country(samples):
    doc = Document(samples("example.odt"))
    doc.language = "en"
    assert doc.styles.default_language == "en"


def test_set_lang_bad(samples):
    doc = Document(samples("example.odt"))
    with pytest.raises(TypeError):
        doc.language = "wrong"


def test_set_lang_bad_2(samples):
    doc = Document(samples("example.odt"))
    with pytest.raises(TypeError):
        doc.language = ""
