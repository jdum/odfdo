# Copyright 2018-2024 Jérôme Dumonteil
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
#          David Versmisse <david.versmisse@itaapy.com>

import io
from collections.abc import Iterable
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from odfdo.const import ODF_META
from odfdo.datatype import DateTime, Duration
from odfdo.document import Document
from odfdo.meta import GENERATOR
from odfdo.meta_auto_reload import MetaAutoReload
from odfdo.meta_hyperlink_behaviour import MetaHyperlinkBehaviour
from odfdo.meta_template import MetaTemplate

META_DOC = Path(__file__).parent / "samples" / "meta.odt"


@pytest.fixture
def meta() -> Iterable:
    document = Document(META_DOC)
    yield document.get_part(ODF_META)


def test_get_title(meta):
    title = meta.get_title()
    expected = "Intitulé"
    assert title == expected


def test_set_title(meta):
    clone = meta.clone
    title = "Nouvel intitulé"
    clone.set_title(title)
    assert clone.get_title() == title


def test_title_property(meta):
    clone = meta.clone
    title = "Nouvel intitulé"
    clone.title = title
    assert clone.title == title


def test_get_description(meta):
    description = meta.get_description()
    expected = "Comments\nCommentaires\n评论"
    assert description == expected


def test_set_description(meta):
    clone = meta.clone
    description = "评论\nnCommentaires\nComments"
    clone.set_description(description)
    assert clone.get_description() == description


def test_description_property(meta):
    clone = meta.clone
    description = "评论\nnCommentaires\nComments"
    clone.description = description
    assert clone.description == description


def test_get_subject(meta):
    subject = meta.get_subject()
    expected = "Sujet de sa majesté"
    assert subject == expected


def test_set_subject(meta):
    clone = meta.clone
    subject = "Θέμα"
    clone.set_subject(subject)
    assert clone.get_subject() == subject


def test_subject_property(meta):
    clone = meta.clone
    subject = "Θέμα"
    clone.subject = subject
    assert clone.subject == subject


def test_get_language(meta):
    language = meta.get_language()
    assert language is None


def test_set_language(meta):
    clone = meta.clone
    language = "en-US"
    clone.set_language(language)
    assert clone.get_language() == language


def test_set_bad_language(meta):
    clone = meta.clone
    language = "English"
    with pytest.raises(TypeError):
        clone.set_language(language)


def test_language_property(meta):
    clone = meta.clone
    language = "en-US"
    clone.language = language
    assert clone.language == language
    assert clone.get_language() == language


def test_get_modification_date(meta):
    date = meta.get_modification_date()
    expected = DateTime.decode("2009-07-31T15:59:13")
    assert date == expected
    assert meta.date == expected


def test_set_modification_date(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.set_modification_date(now)
    assert clone.get_modification_date() == now


def test_modification_date_property(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.date = now
    assert clone.date == now
    assert clone.get_modification_date() == now


def test_set_bad_modication_date(meta):
    clone = meta.clone
    date = "2009-06-29T14:15:45"
    with pytest.raises(AttributeError):
        clone.set_modification_date(date)


def test_print_date_property(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.print_date = now
    assert clone.print_date == now


def test_get_creation_date(meta):
    date = meta.get_creation_date()
    expected = datetime(2009, 7, 31, 15, 57, 37)
    assert date == expected


def test_set_creation_date(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.set_creation_date(now)
    assert clone.get_creation_date() == now


def test_set_bad_creation_date(meta):
    clone = meta.clone
    date = "2009-06-29T14:15:45"
    with pytest.raises(AttributeError):
        clone.set_creation_date(date)


def test_creation_date_property(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.creation_date = now
    assert clone.creation_date == now


def test_get_initial_creator(meta):
    creator = meta.get_initial_creator()
    expected = None
    assert creator == expected


def test_set_initial_creator(meta):
    clone = meta.clone
    creator = "Hervé"
    clone.set_initial_creator(creator)
    assert clone.get_initial_creator() == creator


def test_initial_creator_property(meta):
    clone = meta.clone
    creator = "Hervé"
    clone.initial_creator = creator
    assert clone.initial_creator == creator


def test_printed_by_property(meta):
    clone = meta.clone
    printer = "Jérôme"
    clone.printed_by = printer
    assert clone.printed_by == printer


def test_get_creator(meta):
    creator = meta.creator
    expected = None
    assert creator == expected


def test_set_creator(meta):
    clone = meta.clone
    creator = "Hervé"
    clone.creator = creator
    assert clone.creator == creator


def test_get_keywords(meta):
    keywords = meta.get_keywords()
    expected = "Mots-clés"
    assert keywords == expected


def test_set_keywords(meta):
    clone = meta.clone
    keywords = "Nouveaux mots-clés"
    clone.set_keywords(keywords)
    assert clone.get_keywords() == keywords


def test_keyword_property(meta):
    clone = meta.clone
    keywords = "Nouveaux mots-clés"
    clone.keyword = keywords
    assert clone.keyword == keywords


def test_keywords_property(meta):
    clone = meta.clone
    keywords = "Nouveaux mots-clés"
    clone.keywords = keywords
    assert clone.keywords == keywords


def test_get_editing_duration(meta):
    duration = meta.get_editing_duration()
    expected = Duration.decode("PT00H05M30S")
    assert duration == expected


def test_set_editing_duration(meta):
    clone = meta.clone
    duration = timedelta(1, 2, 0, 0, 5, 6, 7)
    clone.set_editing_duration(duration)
    assert clone.get_editing_duration() == duration


def test_set_bad_editing_duration(meta):
    clone = meta.clone
    duration = "PT00H01M27S"
    with pytest.raises(TypeError):
        clone.set_editing_duration(duration)


def test_get_editing_cycles(meta):
    cycles = meta.get_editing_cycles()
    expected = 2
    assert cycles == expected


def test_set_editing_cycles(meta):
    clone = meta.clone
    cycles = 1  # I swear it was a first shot!
    clone.set_editing_cycles(cycles)
    assert clone.get_editing_cycles() == cycles


def test_set_bad_editing_cycles(meta):
    clone = meta.clone
    cycles = "3"
    with pytest.raises(TypeError):
        clone.set_editing_duration(cycles)


def test_get_generator(meta):
    generator = meta.get_generator()
    expected = (
        "LibreOffice/6.0.3.2$MacOSX_X86_64 "
        "LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821"
    )
    assert generator == expected


def test_generator_getter(meta):
    generator = meta.generator
    expected = (
        "LibreOffice/6.0.3.2$MacOSX_X86_64 "
        "LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821"
    )
    assert generator == expected


def test_set_generator(meta):
    clone = meta.clone
    generator = "odfdo Project"
    clone.set_generator(generator)
    assert clone.get_generator() == generator


def test_generator_setter(meta):
    clone = meta.clone
    generator = "odfdo Project"
    clone.generator = generator
    assert clone.generator == generator


def test_generator_default_unmodified():
    document = Document(META_DOC)
    with io.BytesIO() as bytes_content:
        document.save(bytes_content)
    # document saved, generator string should be ours
    assert document.meta.get_generator() == GENERATOR


def test_generator_default_modified():
    document = Document(META_DOC)
    document.meta.set_generator("custom generator")
    with io.BytesIO() as bytes_content:
        document.save(bytes_content)
    # document saved, generator string should be untouched
    assert document.meta.get_generator() == "custom generator"


def test_get_statistic(meta):
    statistic = meta.get_statistic()
    expected = {
        "meta:table-count": 0,
        "meta:image-count": 0,
        "meta:object-count": 0,
        "meta:page-count": 1,
        "meta:paragraph-count": 1,
        "meta:word-count": 4,
        "meta:character-count": 27,
        "meta:non-whitespace-character-count": 24,
    }
    assert statistic == expected


def test_set_statistic(meta):
    clone = meta.clone
    statistic = {
        "meta:table-count": 1,
        "meta:image-count": 2,
        "meta:object-count": 3,
        "meta:page-count": 4,
        "meta:paragraph-count": 5,
        "meta:word-count": 6,
        "meta:character-count": 7,
        "meta:non-whitespace-character-count": 24,
    }
    clone.set_statistic(statistic)
    assert clone.get_statistic() == statistic


def test_get_user_defined_metadata(meta):
    metadata = meta.get_user_defined_metadata()
    expected = {
        "Achevé à la date": datetime(2009, 7, 31),
        "Numéro du document": Decimal("3"),
        "Référence": True,
        "Vérifié par": "Moi-même",
    }
    assert metadata == expected


def test_set_user_defined_metadata(meta):
    # A new value
    meta.set_user_defined_metadata("Prop5", 1)
    # Change a value
    meta.set_user_defined_metadata("Référence", False)
    expected = {
        "Achevé à la date": datetime(2009, 7, 31),
        "Numéro du document": Decimal("3"),
        "Référence": False,
        "Vérifié par": "Moi-même",
        "Prop5": Decimal("1"),
    }
    metadata = meta.get_user_defined_metadata()
    assert metadata == expected


def test_get_user_defined_metadata_of_name(meta):
    ref = "Référence"
    metadata = meta.get_user_defined_metadata_of_name(ref)
    expected = {"name": ref, "text": "true", "value": True, "value_type": "boolean"}
    assert metadata == expected


def test_no_meta_template(meta):
    clone = meta.clone
    template = clone.template
    assert template is None


def test_set_meta_template(meta):
    clone = meta.clone
    now = datetime.now().replace(microsecond=0)
    clone.set_template(date=now, href="some url", title="some title")
    template = clone.template
    assert isinstance(template, MetaTemplate)
    assert template.date == DateTime.encode(now)
    assert template.href == "some url"
    assert template.title == "some title"


def test_no_meta_auto_reload(meta):
    clone = meta.clone
    reload = clone.auto_reload
    assert reload is None


def test_set_meta_auto_reload(meta):
    clone = meta.clone
    delay = timedelta(seconds=15)
    clone.set_auto_reload(delay=delay, href="some url")
    reload = clone.auto_reload
    assert isinstance(reload, MetaAutoReload)
    assert reload.delay == Duration.encode(delay)
    assert reload.href == "some url"
    assert repr(reload) == (
        "<MetaAutoReload tag=meta:auto-reload href=some url delay=0:00:15>"
    )


def test_no_hyperlink_behaviour(meta):
    clone = meta.clone
    behaviour = clone.hyperlink_behaviour
    assert behaviour is None


def test_set_hyperlink_behaviour(meta):
    clone = meta.clone
    clone.set_hyperlink_behaviour(target_frame_name="some_frame", show="_top")
    behaviour = clone.hyperlink_behaviour
    assert isinstance(behaviour, MetaHyperlinkBehaviour)
    assert behaviour.show == "_top"
    assert behaviour.target_frame_name == "some_frame"
    assert repr(behaviour) == (
        "<MetaHyperlinkBehaviour tag=meta:hyperlink-behaviour target=some_frame show=_top>"
    )
