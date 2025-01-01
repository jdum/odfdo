# Copyright 2018-2025 Jérôme Dumonteil
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
"""Mixin class for <dc:creator>.
"""
from __future__ import annotations

from .element import Element


class DcCreatorMixin:
    def get_creator(self) -> str | None:
        """Get the creator of the document.

        (Also available as "self.creator" property.)

        Return: str (or None if inexistant)

        Example::

            >>> document.meta.get_creator()
            Unknown
        """
        element = self.get_element("//dc:creator")
        if element is None:
            return None
        return element.text

    def set_creator(self, creator: str) -> None:
        """Set the creator of the document.

        (Also available as "self.creator" property.)

        Arguments:

            creator -- str

        Example::

            >>> document.meta.set_creator("Plato")
        """
        element = self.get_element("//dc:creator")
        if element is None:
            element = Element.from_tag("dc:creator")
            if hasattr(self, "get_meta_body"):
                self.get_meta_body().append(element)
            else:
                self.append(element)
        element.text = creator

    @property
    def creator(self) -> str | None:
        """Get or set the <dc:creator> element.

        The <dc:creator> element specifies the name of the person who last
        modified a document (<office:meta>), who created an annotation
        (<office:annotation>), who authored a change (<office:change-info>).

        The <dc:creator> element is usable within the following elements:
        <office:annotation>, <office:change-info> and <office:meta>.
        """
        return self.get_creator()

    @creator.setter
    def creator(self, creator: str) -> None:
        self.set_creator(creator)
