# Copyright 2018-2020 Jérôme Dumonteil
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
"""Section class for "text:section"
"""
from .element import Element, register_element_class


class Section(Element):
    """ODF section "text:section"

    Arguments:

        style -- str

        name -- str

    Return: Section
    """

    _tag = "text:section"
    _properties = (
        ("style", "text:style-name"),
        ("name", "text:name"),
    )

    def __init__(self, style=None, name=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if style:
                self.style = style
            if name:
                self.name = name

    def get_formatted_text(self, context):
        result = []
        for element in self.children:
            result.append(element.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


Section._define_attribut_property()

register_element_class(Section)
