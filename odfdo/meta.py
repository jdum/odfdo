# Copyright 2018-2020 Jérôme Dumonteil
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
"""Meta class for meta.xml part
"""
from datetime import timedelta, datetime
from datetime import date as dtdate
from decimal import Decimal
from string import ascii_letters, digits

from .datatype import DateTime, Duration, Boolean, Date
from .element import Element
from .xmlpart import XmlPart
from .utils import to_str
from .version import __version__


class Meta(XmlPart):
    _generator_modified = False

    def get_meta_body(self):
        return self.get_element("//office:meta")

    def get_title(self):
        """Get the title of the document.

        This is not the first heading but the title metadata.

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:title")
        if element is None:
            return None
        return element.text

    def set_title(self, title):
        """Set the title of the document.

        This is not the first heading but the title metadata.

        Arguments:

            title -- str
        """
        element = self.get_element("//dc:title")
        if element is None:
            element = Element.from_tag("dc:title")
            self.get_meta_body().append(element)
        element.text = title

    def get_description(self):
        """Get the description of the document. Also known as comments.

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:description")
        if element is None:
            return None
        return element.text

    # As named in OOo
    get_comments = get_description

    def set_description(self, description):
        """Set the description of the document. Also known as comments.

        Arguments:

            description -- str
        """
        element = self.get_element("//dc:description")
        if element is None:
            element = Element.from_tag("dc:description")
            self.get_meta_body().append(element)
        element.text = description

    set_comments = set_description

    def get_subject(self):
        """Get the subject of the document.

        Return: str (or None if inexistant)
        """
        element = self.get_element("//dc:subject")
        if element is None:
            return None
        return element.text

    def set_subject(self, subject):
        """Set the subject of the document.

        Arguments:

            subject -- str
        """
        element = self.get_element("//dc:subject")
        if element is None:
            element = Element.from_tag("dc:subject")
            self.get_meta_body().append(element)
        element.text = subject

    def get_language(self):
        """Get the language code of the document.

        Return: str (or None if inexistant)

        Example::

            >>> document.get_language()
            fr-FR
        """
        element = self.get_element("//dc:language")
        if element is None:
            return None
        return element.text

    def set_language(self, language):
        """Set the language code of the document.

        Arguments:

            language -- str

        Example::

            >>> document.set_language('fr-FR')
        """
        language = to_str(language)
        if not self._is_RFC3066(language):
            raise TypeError('language must be "xx-YY" lang-COUNTRY code (RFC3066)')
        element = self.get_element("//dc:language")
        if element is None:
            element = Element.from_tag("dc:language")
            self.get_meta_body().append(element)
        element.text = language

    @staticmethod
    def _is_RFC3066(lang):
        def test_part1(p1):
            if not 2 <= len(p1) <= 3:
                return False
            for x in p1:
                if x not in ascii_letters:
                    return False
            return True

        def test_part2(p1):
            for x in p1:
                if x not in ascii_letters and x not in digits:
                    return False
            return True

        if not lang or not isinstance(lang, str):
            return False
        if "-" not in lang:
            return test_part1(lang)
        parts = lang.split("-")
        if len(parts) > 3:
            return False
        if not test_part1(parts[0]):
            return False
        for p in parts[1:]:
            if not test_part2(p):
                return False
        return True

    def get_modification_date(self):
        """Get the last modified date of the document.

        Return: datetime (or None if inexistant)
        """
        element = self.get_element("//dc:date")
        if element is None:
            return None
        modification_date = element.text
        return DateTime.decode(modification_date)

    def set_modification_date(self, date):
        """Set the last modified date of the document.

        Arguments:

            date -- datetime
        """
        element = self.get_element("//dc:date")
        if element is None:
            element = Element.from_tag("dc:date")
            self.get_meta_body().append(element)
        element.text = DateTime.encode(date)

    def get_creation_date(self):
        """Get the creation date of the document.

        Return: datetime (or None if inexistant)
        """
        element = self.get_element("//meta:creation-date")
        if element is None:
            return None
        creation_date = element.text
        return DateTime.decode(creation_date)

    def set_creation_date(self, date):
        """Set the creation date of the document.

        Arguments:

            date -- datetime
        """
        element = self.get_element("//meta:creation-date")
        if element is None:
            element = Element.from_tag("meta:creation-date")
            self.get_meta_body().append(element)
        element.text = DateTime.encode(date)

    def get_initial_creator(self):
        """Get the first creator of the document.

        Return: str (or None if inexistant)

        Example::

            >>> document.get_initial_creator()
            Unknown
        """
        element = self.get_element("//meta:initial-creator")
        if element is None:
            return None
        return element.text

    def set_initial_creator(self, creator):
        """Set the first creator of the document.

        Arguments:

            creator -- str

        Example::

            >>> document.set_initial_creator(u"Plato")
        """
        element = self.get_element("//meta:initial-creator")
        if element is None:
            element = Element.from_tag("meta:initial-creator")
            self.get_meta_body().append(element)
        element.text = creator

    def get_creator(self):
        """Get the creator of the document.

        Return: str (or None if inexistant)

        Example::

            >>> document.get_creator()
            Unknown
        """
        element = self.get_element("//dc:creator")
        if element is None:
            return None
        return element.text

    def set_creator(self, creator):
        """Set the creator of the document.

        Arguments:

            creator -- str

        Example::

            >>> document.set_creator(u"Plato")
        """
        element = self.get_element("//dc:creator")
        if element is None:
            element = Element.from_tag("dc:creator")
            self.get_meta_body().append(element)
        element.text = creator

    def get_keywords(self):
        """Get the keywords of the document. Return the field as-is, without
        any assumption on the keyword separator.

        Return: str (or None if inexistant)
        """
        element = self.get_element("//meta:keyword")
        if element is None:
            return None
        return element.text

    def set_keywords(self, keywords):
        """Set the keywords of the document. Although the name is plural, a
        str string is required, so join your list first.

        Arguments:

            keywords -- str
        """
        element = self.get_element("//meta:keyword")
        if element is None:
            element = Element.from_tag("meta:keyword")
            self.get_meta_body().append(element)
        element.text = keywords

    def get_editing_duration(self):
        """Get the time the document was edited, as reported by the
        generator.

        Return: timedelta (or None if inexistant)
        """
        element = self.get_element("//meta:editing-duration")
        if element is None:
            return None
        duration = element.text
        return Duration.decode(duration)

    def set_editing_duration(self, duration):
        """Set the time the document was edited.

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

    def get_editing_cycles(self):
        """Get the number of times the document was edited, as reported by
        the generator.

        Return: int (or None if inexistant)
        """
        element = self.get_element("//meta:editing-cycles")
        if element is None:
            return None
        cycles = element.text
        return int(cycles)

    def set_editing_cycles(self, cycles):
        """Set the number of times the document was edited.

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

    def get_generator(self):
        """Get the signature of the software that generated this document.

        Return: str (or None if inexistant)

        Example::

            >>> document.get_generator()
            KOffice/2.0.0
        """
        element = self.get_element("//meta:generator")
        if element is None:
            return None
        return element.text

    def set_generator(self, generator):
        """Set the signature of the software that generated this document.

        Arguments:

            generator -- str

        Example::

            >>> document.set_generator(u"lpOD Project")
        """
        element = self.get_element("//meta:generator")
        if element is None:
            element = Element.from_tag("meta:generator")
            self.get_meta_body().append(element)
        element.text = generator
        self._generator_modified = True

    def set_generator_default(self):
        """Set the signature of the software that generated this document
        to ourself.

        Example::

            >>> document.set_generator_default()
        """
        if not self._generator_modified:
            self.set_generator("odfdo %s" % __version__)

    def get_statistic(self):
        """Get the statistic from the software that generated this document.

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

    def set_statistic(self, statistic):
        """Set the statistic for the documents: number of words, paragraphs,
        etc.

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
            >>> document.set_statistic(statistic)
        """
        if not isinstance(statistic, dict):
            raise TypeError("statistic must be a dict")
        element = self.get_element("//meta:document-statistic")
        for key, value in statistic.items():
            try:
                ivalue = int(value)
            except ValueError:
                raise TypeError("statistic value must be a int")
            element.set_attribute(to_str(key), str(ivalue))

    def get_user_defined_metadata(self):
        """Return a dict of str/value mapping.

        Value types can be: Decimal, date, time, boolean or str.
        """
        result = {}
        for item in self.get_elements("//meta:user-defined"):
            # Read the values
            name = item.get_attribute("meta:name")
            value = self._get_meta_value(item)
            result[name] = value
        return result

    def get_user_defined_metadata_of_name(self, keyname):
        """Return the content of the user defined metadata of that name.
        Return None if no name matchs or a dic of fields.

        Arguments:

            name -- string, name (meta:name content)
        """
        result = {}
        found = False
        for item in self.get_elements("//meta:user-defined"):
            # Read the values
            name = item.get_attribute("meta:name")
            if name == keyname:
                found = True
                break
        if not found:
            return None
        result["name"] = name
        value, value_type, text = self._get_meta_value(item, full=True)
        result["value"] = value
        result["value_type"] = value_type
        result["text"] = text
        return result

    def set_user_defined_metadata(self, name, value):
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
            raise TypeError('unexpected type "%s" for value' % type(value))
        # Already the same element ?
        for metadata in self.get_elements("//meta:user-defined"):
            if metadata.get_attribute("meta:name") == name:
                break
        else:
            metadata = Element.from_tag("meta:user-defined")
            metadata.set_attribute("meta:name", name)
            self.get_meta_body().append(metadata)
        metadata.set_attribute("meta:value-type", value_type)
        metadata.text = value

    @staticmethod
    def _get_meta_value(element, full=False):
        """get_value deicated to the meta data part, for one meta element."""
        # name = element.get_attribute('meta:name')
        value_type = element.get_attribute("meta:value-type")
        if value_type is None:
            value_type = "string"
        text = element.text
        # Interpretation
        if value_type == "boolean":
            value = Boolean.decode(text)
        elif value_type in ("float", "percentage", "currency"):
            value = Decimal(text)
        elif value_type == "date":
            if "T" in text:
                value = DateTime.decode(text)
            else:
                value = Date.decode(text)
        elif value_type == "string":
            value = text
        elif value_type == "time":
            value = Duration.decode(text)
        if full:
            return (value, value_type, text)
        else:
            return value
