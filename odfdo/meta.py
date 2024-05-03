# Copyright 2018-2024 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Meta class for meta.xml part.
"""
from __future__ import annotations

from datetime import date as dtdate
from datetime import datetime, timedelta
from decimal import Decimal
from string import ascii_letters, digits
from typing import Any

from .datatype import Boolean, Date, DateTime, Duration
from .element import Element
from .meta_auto_reload import MetaAutoReload
from .meta_hyperlink_behaviour import MetaHyperlinkBehaviour
from .meta_template import MetaTemplate
from .mixin_dc_creator import DcCreatorMixin
from .mixin_dc_date import DcDateMixin
from .utils import to_str
from .version import __version__
from .xmlpart import XmlPart

GENERATOR = f"odfdo {__version__}"


class Meta(XmlPart, DcCreatorMixin, DcDateMixin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._generator_modified: bool = False

    def get_meta_body(self) -> Element:
        return self.get_element("//office:meta")

    def get_title(self) -> str | None:
        """Get the title of the document.

        This is not the first heading but the title metadata.

        (Also available as "self.title" property.)

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:title")
        if element is None:
            return None
        return element.text

    def set_title(self, title: str) -> None:
        """Set the title of the document.

        This is not the first heading but the title metadata.

        (Also available as "self.title" property.)

        Arguments:

            title -- str
        """
        element = self.get_element("//dc:title")
        if element is None:
            element = Element.from_tag("dc:title")
            self.get_meta_body().append(element)
        element.text = title

    @property
    def title(self) -> str | None:
        """Get or set the title of the document <dc:title>.

        Return: str (or None if inexistant)
        """
        return self.get_title()

    @title.setter
    def title(self, title: str) -> None:
        return self.set_title(title)

    def get_description(self) -> str | None:
        """Get the description of the document. Also known as comments.

        (Also available as "self.description" property.)

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:description")
        if element is None:
            return None
        return element.text

    # As named in OOo
    get_comments = get_description

    def set_description(self, description: str) -> None:
        """Set the description of the document. Also known as comments.

        (Also available as "self.description" property.)

        Arguments:

            description -- str
        """
        element = self.get_element("//dc:description")
        if element is None:
            element = Element.from_tag("dc:description")
            self.get_meta_body().append(element)
        element.text = description

    set_comments = set_description

    @property
    def description(self) -> str | None:
        """Get or set the description of a document <dc:description>.

        Return: str (or None if inexistant)
        """
        return self.get_description()

    @description.setter
    def description(self, description: str) -> None:
        return self.set_description(description)

    def get_subject(self) -> str | None:
        """Get the subject of the document.

        (Also available as "self.subject" property.)

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:subject")
        if element is None:
            return None
        return element.text

    def set_subject(self, subject: str) -> None:
        """Set the subject of the document.

        (Also available as "self.subject" property.)

        Arguments:

            subject -- str
        """
        element = self.get_element("//dc:subject")
        if element is None:
            element = Element.from_tag("dc:subject")
            self.get_meta_body().append(element)
        element.text = subject

    @property
    def subject(self) -> str | None:
        """Get or set the subject of a document <dc:subject>.

        Return: str (or None if inexistant)
        """
        return self.get_subject()

    @subject.setter
    def subject(self, subject: str) -> None:
        return self.set_subject(subject)

    def get_language(self) -> str | None:
        """Get the default language of the document.

        (Also available as "self.language" property.)

        Return: str (or None if inexistant)

        Example::

            >>> document.meta.get_language()
            fr-FR
        """
        element = self.get_element("//dc:language")
        if element is None:
            return None
        return element.text

    def set_language(self, language: str) -> None:
        """Set the default language of the document.

        (Also available as "self.language" property.)

        Arguments:

            language -- str

        Example::

            >>> document.meta.set_language('fr-FR')
        """
        language = str(language)
        if not self._is_RFC3066(language):
            raise TypeError(
                'Language must be "xx" lang or "xx-YY" lang-COUNTRY code (RFC3066)'
            )
        element = self.get_element("//dc:language")
        if element is None:
            element = Element.from_tag("dc:language")
            self.get_meta_body().append(element)
        element.text = language

    @staticmethod
    def _is_RFC3066(lang: str) -> bool:
        def test_part1(part1: str) -> bool:
            if not 2 <= len(part1) <= 3:
                return False
            return all(x in ascii_letters for x in part1)

        def test_part2(part2: str) -> bool:
            return all(x in ascii_letters or x in digits for x in part2)

        if not lang or not isinstance(lang, str):
            return False
        if "-" not in lang:
            return test_part1(lang)
        parts = lang.split("-")
        if len(parts) > 3:
            return False
        if not test_part1(parts[0]):
            return False
        return all(test_part2(p) for p in parts[1:])

    @property
    def language(self) -> str | None:
        """Get or set the default language of the document <dc:language>.

        Return: str (or None if inexistant)
        """
        return self.get_language()

    @language.setter
    def language(self, language: str) -> None:
        return self.set_language(language)

    def get_creation_date(self) -> datetime | None:
        """Get the creation date of the document.

        (Also available as "self.creation_date" property.)

        Return: datetime (or None if inexistant)
        """
        element = self.get_element("//meta:creation-date")
        if element is None:
            return None
        creation_date = element.text
        return DateTime.decode(creation_date)

    def set_creation_date(self, date: datetime | None = None) -> None:
        """Set the creation date of the document.

        If provided datetime is None, use current time.

        (Also available as "self.creation_date" property.)

        Arguments:

            date -- datetime
        """
        element = self.get_element("//meta:creation-date")
        if element is None:
            element = Element.from_tag("meta:creation-date")
            self.get_meta_body().append(element)
        if date is None:
            date = datetime.now()
        element.text = DateTime.encode(date)

    @property
    def creation_date(self) -> datetime | None:
        """Get or set the date and time when a document was created
        <meta:creation-date>.

        If provided datetime is None, use current time.

        Return: datetime (or None if inexistant)
        """
        return self.get_creation_date()

    @creation_date.setter
    def creation_date(self, date: datetime | None = None) -> None:
        return self.set_creation_date(date)

    @property
    def print_date(self) -> datetime | None:
        """Get or set the date and time when a document when a document was last printed
        <meta:print-date>

        If provided datetime is None, use current time.

        Return: datetime (or None if inexistant)
        """
        element = self.get_element("//meta:print-date")
        if element is None:
            return None
        date = element.text
        return DateTime.decode(date)

    @print_date.setter
    def print_date(self, date: datetime | None = None) -> None:
        element = self.get_element("//meta:print-date")
        if element is None:
            element = Element.from_tag("meta:print-date")
            self.get_meta_body().append(element)
        if date is None:
            date = datetime.now()
        element.text = DateTime.encode(date)

    def get_template(self) -> MetaTemplate | None:
        """Get the MetaTemplate <meta:template> element or None."""
        element = self.get_element("//meta:template")
        if element is None:
            return None
        return element

    @property
    def template(self) -> MetaTemplate | None:
        """Get the MetaTemplate <meta:template> element or None."""
        return self.get_template()

    def set_template(
        self,
        date: datetime | None = None,
        href: str = "",
        title: str = "",
    ) -> None:
        """Set the MetaTemplate <meta:template> element."""
        template = MetaTemplate(date=date, href=href, title=title)
        current = self.template
        if isinstance(current, MetaTemplate):
            current.delete()
        self.get_meta_body().append(template)

    def get_auto_reload(self) -> MetaAutoReload | None:
        """Get the MetaAutoReload <meta:auto-reload> element or None."""
        element = self.get_element("//meta:auto-reload")
        if element is None:
            return None
        return element

    @property
    def auto_reload(self) -> MetaAutoReload | None:
        """Get the MetaAutoReload <meta:auto-reload> element or None."""
        return self.get_auto_reload()

    def set_auto_reload(self, delay: timedelta, href: str = "") -> None:
        """Set the MetaAutoReload <meta:auto-reload> element."""
        autoreload = MetaAutoReload(delay=delay, href=href)
        current = self.auto_reload
        if isinstance(current, MetaAutoReload):
            current.delete()
        self.get_meta_body().append(autoreload)

    def get_hyperlink_behaviour(self) -> MetaHyperlinkBehaviour | None:
        """Get the MetaHyperlinkBehaviour <meta:hyperlink-behaviour> element or None."""
        element = self.get_element("//meta:hyperlink-behaviour")
        if element is None:
            return None
        return element

    @property
    def hyperlink_behaviour(self) -> MetaAutoReload | None:
        """Get the MetaHyperlinkBehaviour <meta:hyperlink-behaviour> element or None."""
        return self.get_hyperlink_behaviour()

    def set_hyperlink_behaviour(
        self,
        target_frame_name: str = "_blank",
        show: str = "replace",
    ) -> None:
        """Set the MetaHyperlinkBehaviour <meta:hyperlink-behaviour> element."""
        behaviour = MetaHyperlinkBehaviour(
            target_frame_name=target_frame_name, show=show
        )
        current = self.hyperlink_behaviour
        if isinstance(current, MetaHyperlinkBehaviour):
            current.delete()
        self.get_meta_body().append(behaviour)

    def get_initial_creator(self) -> str | None:
        """Get the first creator of the document.

        (Also available as "self.initial_creator" property.)

        Return: str (or None if inexistant)

        Example::

            >>> document.meta.get_initial_creator()
            Unknown
        """
        element = self.get_element("//meta:initial-creator")
        if element is None:
            return None
        return element.text

    def set_initial_creator(self, creator: str) -> None:
        """Set the first creator of the document.

        (Also available as "self.initial_creator" property.)

        Arguments:

            creator -- str

        Example::

            >>> document.meta.set_initial_creator("Plato")
        """
        element = self.get_element("//meta:initial-creator")
        if element is None:
            element = Element.from_tag("meta:initial-creator")
            self.get_meta_body().append(element)
        element.text = creator

    @property
    def initial_creator(self) -> str | None:
        """Get or set the initial creator of a document
        <meta:initial-creator>.

        Return: str (or None if inexistant)
        """
        return self.get_initial_creator()

    @initial_creator.setter
    def initial_creator(self, creator: str) -> None:
        return self.set_initial_creator(creator)

    @property
    def printed_by(self) -> str | None:
        """Get or set the name of the last person who printed a document.
        <meta:printed-by>

        Return: str (or None if inexistant)
        """
        element = self.get_element("//meta:printed-by")
        if element is None:
            return None
        return element.text

    @printed_by.setter
    def printed_by(self, printed_by: str) -> None:
        element = self.get_element("//meta:printed-by")
        if element is None:
            element = Element.from_tag("meta:printed-by")
            self.get_meta_body().append(element)
        element.text = printed_by

    def get_keywords(self) -> str | None:
        """Get the keywords of the document. Return the field as-is, without
        any assumption on the keyword separator.

        (Also available as "self.keyword" and "self.keywords" property.)

        Return: str (or None if inexistant)
        """
        element = self.get_element("//meta:keyword")
        if element is None:
            return None
        return element.text

    def set_keywords(self, keywords: str) -> None:
        """Set the keywords of the document. Although the name is plural, a
        str string is required, so join your list first.

        (Also available as "self.keyword" and "self.keywords" property.)

        Arguments:

            keywords -- str
        """
        element = self.get_element("//meta:keyword")
        if element is None:
            element = Element.from_tag("meta:keyword")
            self.get_meta_body().append(element)
        element.text = keywords

    @property
    def keyword(self) -> str | None:
        """Get or set some keyword(s) keyword pertaining to a document
        <dc:keyword>.

        Return: str (or None if inexistant)
        """
        return self.get_keywords()

    @keyword.setter
    def keyword(self, keyword: str) -> None:
        return self.set_keywords(keyword)

    keywords = keyword

    def get_editing_duration(self) -> timedelta | None:
        """Get the time the document was edited, as reported by the
        generator.

        (Also available as "self.editing_duration" property.)

        Return: timedelta (or None if inexistant)
        """
        element = self.get_element("//meta:editing-duration")
        if element is None:
            return None
        duration = element.text
        return Duration.decode(duration)

    def set_editing_duration(self, duration: timedelta) -> None:
        """Set the time the document was edited.

        (Also available as "self.editing_duration" property.)

        Arguments:

            duration -- timedelta
        """
        if not isinstance(duration, timedelta):
            raise TypeError("duration must be a timedelta")
        element = self.get_element("//meta:editing-duration")
        if element is None:
            element = Element.from_tag("meta:editing-duration")
            self.get_meta_body().append(element)
        element.text = Duration.encode(duration)

    @property
    def editing_duration(self) -> timedelta | None:
        """Get or set the total time spent editing a document
        <meta:editing-duration>.

        Return: timedelta (or None if inexistant)
        """
        return self.get_editing_duration()

    @editing_duration.setter
    def editing_duration(self, duration: timedelta) -> None:
        return self.set_editing_duration(duration)

    def get_editing_cycles(self) -> int | None:
        """Get the number of times the document was edited, as reported by
        the generator.

        (Also available as "self.editing_cycles" property.)

        Return: int (or None if inexistant)
        """
        element = self.get_element("//meta:editing-cycles")
        if element is None:
            return None
        cycles = element.text
        return int(cycles)

    def set_editing_cycles(self, cycles: int) -> None:
        """Set the number of times the document was edited.

        (Also available as "self.editing_cycles" property.)

        Arguments:

            cycles -- int
        """
        if not isinstance(cycles, int):
            raise TypeError("cycles must be an int")
        if cycles < 1:
            raise ValueError("cycles must be a positive int")
        element = self.get_element("//meta:editing-cycles")
        if element is None:
            element = Element.from_tag("meta:editing-cycles")
            self.get_meta_body().append(element)
        element.text = str(cycles)

    @property
    def editing_cycles(self) -> int | None:
        """Get or set the number of times a document has been edited
        <meta:editing-cycles>.

        When a document is created, this value is set to 1. Each time
        a document is saved, the editing-cycles number is incremented by 1.

        Return: int (or None if inexistant)
        """
        return self.get_editing_cycles()

    @editing_cycles.setter
    def editing_cycles(self, cycles: int) -> None:
        return self.set_editing_cycles(cycles)

    @property
    def generator(self) -> str | None:
        """Get or set the signature of the software that generated this
        document.

        Return: str (or None if inexistant)

        Example::

            >>> document.meta.generator
            KOffice/2.0.0
            >>> document.meta.generator = "Odfdo experiment"
        """
        element = self.get_element("//meta:generator")
        if element is None:
            return None
        return element.text

    @generator.setter
    def generator(self, generator: str) -> None:
        element = self.get_element("//meta:generator")
        if element is None:
            element = Element.from_tag("meta:generator")
            self.get_meta_body().append(element)
        element.text = generator
        self._generator_modified = True

    def get_generator(self) -> str | None:
        """Get the signature of the software that generated this document.

        (Also available as "self.generator" property.)

        Return: str (or None if inexistant)

        Example::

            >>> document.meta.get_generator()
            KOffice/2.0.0
        """
        return self.generator

    def set_generator(self, generator: str) -> None:
        """Set the signature of the software that generated this document.

        (Also available as "self.generator" property.)

        Arguments:

            generator -- str

        Example::

            >>> document.meta.set_generator("Odfdo experiment")
        """
        self.generator = generator

    def set_generator_default(self) -> None:
        """Set the signature of the software that generated this document
        to ourself.

        Example::

            >>> document.meta.set_generator_default()
        """
        if not self._generator_modified:
            self.generator = GENERATOR

    def get_statistic(self) -> dict[str, int] | None:
        """Get the statistics about a document.

        (Also available as "self.statistic" property.)

        Return: dict (or None if inexistant)

        Example::

            >>> document.get_statistic():
            {'meta:table-count': 1,
             'meta:image-count': 2,
             'meta:object-count': 3,
             'meta:page-count': 4,
             'meta:paragraph-count': 5,
             'meta:word-count': 6,
             'meta:character-count': 7}
        """
        element = self.get_element("//meta:document-statistic")
        if element is None:
            return None
        statistic = {}
        for key, value in element.attributes.items():
            statistic[to_str(key)] = int(value)
        return statistic

    def set_statistic(self, statistic: dict[str, int]) -> None:
        """Set the statistics about a document.

        (Also available as "self.statistic" property.)

        Arguments:

            statistic -- dict

        Example::

            >>> statistic = {'meta:table-count': 1,
                             'meta:image-count': 2,
                             'meta:object-count': 3,
                             'meta:page-count': 4,
                             'meta:paragraph-count': 5,
                             'meta:word-count': 6,
                             'meta:character-count': 7}
            >>> document.meta.set_statistic(statistic)
        """
        if not isinstance(statistic, dict):
            raise TypeError("Statistic must be a dict")
        element = self.get_element("//meta:document-statistic")
        for key, value in statistic.items():
            try:
                ivalue = int(value)
            except ValueError as e:
                raise TypeError("Statistic value must be a int") from e
            element.set_attribute(to_str(key), str(ivalue))

    @property
    def statistic(self) -> dict[str, int] | None:
        """Get or set the statistics about a document
        <meta:document-statistic>.

        Return: dict (or None if inexistant)

        Example::

            >>> document.get_statistic():
            {'meta:table-count': 1,
             'meta:image-count': 2,
             'meta:object-count': 3,
             'meta:page-count': 4,
             'meta:paragraph-count': 5,
             'meta:word-count': 6,
             'meta:character-count': 7}
        """
        return self.get_statistic()

    @statistic.setter
    def statistic(self, statistic: dict[str, int]) -> None:
        return self.set_statistic(statistic)

    def get_user_defined_metadata(self) -> dict[str, Any]:
        """Get all additional user-defined metadata for a document.

        (Also available as "self.user_defined_metadata" property.)

        Return a dict of str/value mapping.

        Value types can be: Decimal, date, time, boolean or str.
        """
        result: dict[str, Any] = {}
        for item in self.get_elements("//meta:user-defined"):
            if not isinstance(item, Element):
                continue
            # Read the values
            name = item.get_attribute_string("meta:name")
            if name is None:
                continue
            value = self._get_meta_value(item)
            result[name] = value
        return result

    def clear_user_defined_metadata(self) -> None:
        """Remove all user-defined metadata."""
        while True:
            element = self.get_element("//meta:user-defined")
            if isinstance(element, Element):
                element.delete()
                continue
            break

    @property
    def user_defined_metadata(self) -> dict[str, Any]:
        """Get or set all additional user-defined metadata for a document.

        Return a dict of str/value mapping.

        Value types can be: Decimal, date, time, boolean or str.
        """
        return self.get_user_defined_metadata()

    @user_defined_metadata.setter
    def user_defined_metadata(self, metadata: dict[str, Any]) -> None:
        self.clear_user_defined_metadata()
        for key, val in metadata.items():
            self.set_user_defined_metadata(name=key, value=val)

    def get_user_defined_metadata_of_name(self, keyname: str) -> dict[str, Any] | None:
        """Return the content of the user defined metadata of that name.
        Return None if no name matchs or a dic of fields.

        Arguments:

            name -- string, name (meta:name content)
        """
        result = {}
        found = False
        for item in self.get_elements("//meta:user-defined"):
            if not isinstance(item, Element):
                continue
            # Read the values
            name = item.get_attribute("meta:name")
            if name == keyname:
                found = True
                break
        if not found:
            return None
        result["name"] = name
        value, value_type, text = self._get_meta_value(item, full=True)  # type: ignore
        result["value"] = value
        result["value_type"] = value_type
        result["text"] = text
        return result

    def set_user_defined_metadata(self, name: str, value: Any) -> None:
        if isinstance(value, bool):
            value_type = "boolean"
            value = "true" if value else "false"
        elif isinstance(value, (int, float, Decimal)):
            value_type = "float"
            value = str(value)
        elif isinstance(value, dtdate):
            value_type = "date"
            value = str(Date.encode(value))
        elif isinstance(value, datetime):
            value_type = "date"
            value = str(DateTime.encode(value))
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, timedelta):
            value_type = "time"
            value = str(Duration.encode(value))
        else:
            raise TypeError(f'unexpected type "{type(value)}" for value')
        # Already the same element ?
        for metadata in self.get_elements("//meta:user-defined"):
            if not isinstance(metadata, Element):
                continue
            if metadata.get_attribute("meta:name") == name:
                break
        else:
            metadata = Element.from_tag("meta:user-defined")
            metadata.set_attribute("meta:name", name)
            self.get_meta_body().append(metadata)
        metadata.set_attribute("meta:value-type", value_type)
        metadata.text = value

    def _get_meta_value(
        self, element: Element, full: bool = False
    ) -> Any | tuple[Any, str, str]:
        """get_value() deicated to the meta data part, for one meta element."""
        if full:
            return self._get_meta_value_full(element)
        else:
            return self._get_meta_value_full(element)[0]

    @staticmethod
    def _get_meta_value_full(element: Element) -> tuple[Any, str, str]:
        """get_value deicated to the meta data part, for one meta element."""
        # name = element.get_attribute('meta:name')
        value_type = element.get_attribute_string("meta:value-type")
        if value_type is None:
            value_type = "string"
        text = element.text
        # Interpretation
        if value_type == "boolean":
            return (Boolean.decode(text), value_type, text)
        if value_type in ("float", "percentage", "currency"):
            return (Decimal(text), value_type, text)
        if value_type == "date":
            if "T" in text:
                return (DateTime.decode(text), value_type, text)
            else:
                return (Date.decode(text), value_type, text)
        if value_type == "string":
            return (text, value_type, text)
        if value_type == "time":
            return (Duration.decode(text), value_type, text)
        raise TypeError(f"Unknown value type: '{value_type!r}'")
