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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>

import io
from collections.abc import Iterable
from datetime import datetime, timedelta
from decimal import Decimal
from textwrap import dedent

import pytest

from odfdo.const import ODF_META
from odfdo.datatype import DateTime, Duration
from odfdo.document import Document
from odfdo.meta import GENERATOR
from odfdo.meta_auto_reload import MetaAutoReload
from odfdo.meta_hyperlink_behaviour import MetaHyperlinkBehaviour
from odfdo.meta_template import MetaTemplate


@pytest.fixture
def meta(samples) -> Iterable:
    document = Document(samples("meta.odt"))
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


def test_set_modification_date_meta_special(meta):
    clone = meta.clone
    elem = clone.get_element("//dc:date")
    elem.delete()
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


def test_set_creator_2(meta):
    clone = meta.clone
    clone.creator = None
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


def test_editing_duration_property(meta):
    clone = meta.clone
    duration = timedelta(1, 2, 0, 0, 5, 6, 7)
    clone.editing_duration = duration
    assert clone.editing_duration == duration
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


def test_editing_cycles_property(meta):
    clone = meta.clone
    cycles = 1  # I swear it was a first shot!
    clone.editing_cycles = cycles
    assert clone.editing_cycles == cycles
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


def test_generator_default_unmodified(samples):
    document = Document(samples("meta.odt"))
    with io.BytesIO() as bytes_content:
        document.save(bytes_content)
    # document saved, generator string should be ours
    assert document.meta.get_generator() == GENERATOR


def test_generator_default_modified(samples):
    document = Document(samples("meta.odt"))
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


def test_statistic_property(meta):
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
    clone.statistic = statistic
    assert clone.statistic == statistic
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


def test_user_defined_metadata_property_getter(meta):
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
    metadata = meta.user_defined_metadata
    assert metadata == expected


def test_user_defined_metadata_clear(meta):
    meta.clear_user_defined_metadata()
    metadata = meta.user_defined_metadata
    assert metadata == {}


def test_user_defined_metadata_property_setter(meta):
    new_data = {
        "Achevé le date": datetime(2012, 7, 31),
        "Numéro document": Decimal("4"),
        "Référence": True,
    }
    meta.user_defined_metadata = new_data
    assert meta.user_defined_metadata == new_data
    assert meta.get_user_defined_metadata() == new_data


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


def test_meta_export_dict(meta):
    exported = meta.as_dict()
    expected = {
        "meta:creation-date": datetime(2009, 7, 31, 15, 57, 37),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=330),
        "meta:editing-cycles": 2,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\nCommentaires\n评论",
        "meta:keyword": "Mots-clés",
        "dc:subject": "Sujet de sa majesté",
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": datetime(2009, 7, 31, 0, 0),
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    print(repr(exported))
    assert exported == expected


def test_meta_export_dict_full(meta):
    exported = meta.as_dict(True)
    expected = {
        "meta:creation-date": datetime(2009, 7, 31, 15, 57, 37),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=330),
        "meta:editing-cycles": 2,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\nCommentaires\n评论",
        "dc:creator": None,
        "meta:keyword": "Mots-clés",
        "dc:subject": "Sujet de sa majesté",
        "dc:language": None,
        "meta:initial-creator": None,
        "meta:print-date": None,
        "meta:printed-by": None,
        "meta:auto-reload": None,
        "meta:hyperlink-behaviour": None,
        "meta:template": None,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": datetime(2009, 7, 31, 0, 0),
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    print(repr(exported))
    assert exported == expected


def test_meta_export_json(meta):
    exported = meta.as_json()
    expected = dedent(
        """\
    {
        "meta:creation-date": "2009-07-31T15:57:37",
        "dc:date": "2009-07-31T15:59:13",
        "meta:editing-duration": "PT00H05M30S",
        "meta:editing-cycles": 2,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\\nCommentaires\\n评论",
        "meta:keyword": "Mots-clés",
        "dc:subject": "Sujet de sa majesté",
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": "2009-07-31T00:00:00"
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": 3
            },
            {
                "meta:name": "Référence",
                "meta:value-type": "boolean",
                "value": true
            },
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même"
            }
        ]
    }"""
    )
    print(exported)
    print(expected)
    assert exported.strip() == expected.strip()


def test_meta_export_json_full(meta):
    exported = meta.as_json(True)
    expected = dedent(
        """\
    {
        "meta:creation-date": "2009-07-31T15:57:37",
        "dc:date": "2009-07-31T15:59:13",
        "meta:editing-duration": "PT00H05M30S",
        "meta:editing-cycles": 2,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\\nCommentaires\\n评论",
        "dc:creator": null,
        "meta:keyword": "Mots-clés",
        "dc:subject": "Sujet de sa majesté",
        "dc:language": null,
        "meta:initial-creator": null,
        "meta:print-date": null,
        "meta:printed-by": null,
        "meta:template": null,
        "meta:auto-reload": null,
        "meta:hyperlink-behaviour": null,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": "2009-07-31T00:00:00"
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": 3
            },
            {
                "meta:name": "Référence",
                "meta:value-type": "boolean",
                "value": true
            },
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même"
            }
        ]
    }"""
    )

    print(exported)
    assert exported == expected


def test_meta_from_dict_1(meta):
    imported = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=100),
        "meta:editing-cycles": 1,
        "dc:subject": None,
    }
    expected = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2024, 7, 14, 12, 00, 00),
        "meta:editing-duration": timedelta(seconds=0),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\nCommentaires\n评论",
        "dc:creator": None,
        "meta:keyword": "Mots-clés",
        "dc:subject": None,
        "dc:language": None,
        "meta:initial-creator": None,
        "meta:print-date": None,
        "meta:printed-by": None,
        "meta:auto-reload": None,
        "meta:hyperlink-behaviour": None,
        "meta:template": None,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": datetime(2009, 7, 31, 0, 0),
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    meta.from_dict(imported)
    result = meta.as_dict(full=True)
    assert result == expected


def test_meta_from_dict_2(meta):
    imported = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=100),
        "meta:editing-cycles": 1,
        "dc:subject": None,
        "meta:user-defined": None,
    }
    expected = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2024, 7, 14, 12, 00, 00),
        "meta:editing-duration": timedelta(seconds=0),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\nCommentaires\n评论",
        "dc:creator": None,
        "meta:keyword": "Mots-clés",
        "dc:subject": None,
        "dc:language": None,
        "meta:initial-creator": None,
        "meta:print-date": None,
        "meta:printed-by": None,
        "meta:auto-reload": None,
        "meta:hyperlink-behaviour": None,
        "meta:template": None,
        "meta:user-defined": [],
    }
    meta.from_dict(imported)
    result = meta.as_dict(full=True)
    assert result == expected


def test_meta_from_dict_3(meta):
    imported = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=100),
        "meta:editing-cycles": 1,
        "dc:subject": None,
        "meta:user-defined": [
            {
                "meta:name": "New property",
                "meta:value-type": "string",
                "value": "Anatole",
            }
        ],
    }
    expected = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2024, 7, 14, 12, 00, 00),
        "meta:editing-duration": timedelta(seconds=0),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        },
        "meta:generator": "LibreOffice/6.0.3.2$MacOSX_X86_64 LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821",
        "dc:title": "Intitulé",
        "dc:description": "Comments\nCommentaires\n评论",
        "dc:creator": None,
        "meta:keyword": "Mots-clés",
        "dc:subject": None,
        "dc:language": None,
        "meta:initial-creator": None,
        "meta:print-date": None,
        "meta:printed-by": None,
        "meta:auto-reload": None,
        "meta:hyperlink-behaviour": None,
        "meta:template": None,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "meta:value-type": "date",
                "value": datetime(2009, 7, 31, 0, 0),
            },
            {
                "meta:name": "New property",
                "meta:value-type": "string",
                "value": "Anatole",
            },
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    meta.from_dict(imported)
    result = meta.as_dict(full=True)
    assert result == expected


def test_meta_from_dict_4(meta):
    imported = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=100),
        "meta:editing-cycles": 1,
        "meta:document-statistic": None,
        "meta:generator": "toto",
        "dc:subject": None,
        "dc:title": None,
        "dc:description": None,
        "dc:keyword": None,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "value": None,
            }
        ],
    }
    expected = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2024, 7, 14, 12, 00, 00),
        "meta:editing-duration": timedelta(seconds=0),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 0,
            "meta:paragraph-count": 0,
            "meta:word-count": 0,
            "meta:character-count": 0,
            "meta:non-whitespace-character-count": 0,
        },
        "meta:generator": "toto",
        "dc:title": None,
        "dc:description": None,
        "dc:creator": None,
        "meta:keyword": "Mots-clés",
        "dc:subject": None,
        "dc:language": None,
        "meta:initial-creator": None,
        "meta:print-date": None,
        "meta:printed-by": None,
        "meta:auto-reload": None,
        "meta:hyperlink-behaviour": None,
        "meta:template": None,
        "meta:user-defined": [
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    meta.from_dict(imported)
    result = meta.as_dict(full=True)
    assert result == expected


def test_meta_from_dict_5(meta):
    imported = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2009, 7, 31, 15, 59, 13),
        "meta:editing-duration": timedelta(seconds=100),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 1,
            "meta:image-count": 22,
            "meta:object-count": 33,
            "meta:page-count": 444,
            "meta:paragraph-count": 555,
            "meta:word-count": 666,
            "meta:character-count": 777,
            "meta:non-whitespace-character-count": 888,
        },
        "meta:generator": "toto",
        "dc:subject": None,
        "dc:title": None,
        "dc:description": None,
        "dc:keyword": None,
        "meta:user-defined": [
            {
                "meta:name": "Achevé à la date",
                "value": None,
            }
        ],
    }
    expected = {
        "meta:creation-date": datetime(2024, 7, 14, 12, 00, 00),
        "dc:date": datetime(2024, 7, 14, 12, 00, 00),
        "meta:editing-cycles": 1,
        "meta:document-statistic": {
            "meta:table-count": 1,
            "meta:image-count": 22,
            "meta:object-count": 33,
            "meta:page-count": 444,
            "meta:paragraph-count": 555,
            "meta:word-count": 666,
            "meta:character-count": 777,
            "meta:non-whitespace-character-count": 888,
        },
        "meta:generator": "toto",
        "meta:keyword": "Mots-clés",
        "meta:user-defined": [
            {
                "meta:name": "Numéro du document",
                "meta:value-type": "float",
                "value": Decimal("3"),
            },
            {"meta:name": "Référence", "meta:value-type": "boolean", "value": True},
            {
                "meta:name": "Vérifié par",
                "meta:value-type": "string",
                "value": "Moi-même",
            },
        ],
    }
    meta.from_dict(imported)
    result = meta.as_dict(full=False)
    assert result == expected
