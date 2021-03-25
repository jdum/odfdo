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
"""DrawPage class for "draw:page"
"""
from .element import register_element_class, Element
from .shapes import registered_shapes
from .smil import AnimPar, AnimTransFilter


class DrawPage(Element):
    """ODF draw page "draw:page", for pages of presentation and drawings."""

    _tag = "draw:page"
    _properties = (
        ("name", "draw:name"),
        ("draw_id", "draw:id"),
        ("master_page", "draw:master-page-name"),
        ("presentation_page_layout", "presentation:presentation-page-layout-name"),
        ("style", "draw:style-name"),
    )

    def __init__(
        self,
        draw_id=None,
        name=None,
        master_page=None,
        presentation_page_layout=None,
        style=None,
        **kw,
    ):
        """
        Arguments:

            draw_id -- str

            name -- str

            master_page -- str

            presentation_page_layout -- str

            style -- str

        Return: DrawPage
        """
        super().__init__(**kw)
        if self._do_init:
            if draw_id:
                self.draw_id = draw_id
            if name:
                self.name = name
            if master_page:
                self.master_page = master_page
            if presentation_page_layout:
                self.presentation_page_layout = presentation_page_layout
            if style:
                self.style = style

    def set_transition(self, smil_type, subtype=None, dur="2s"):
        # Create the new animation
        anim_page = AnimPar(presentation_node_type="timing-root")
        anim_begin = AnimPar(smil_begin=f"{self.draw_id}.begin")
        transition = AnimTransFilter(
            smil_dur=dur, smil_type=smil_type, smil_subtype=subtype
        )
        anim_page.append(anim_begin)
        anim_begin.append(transition)

        # Replace when already a transition:
        #   anim:seq => After the frame's transition
        #   cf page 349 of OpenDocument-v1.0-os.pdf
        #   Conclusion: We must delete the first child 'anim:par'
        existing = self.get_element("anim:par")
        if existing:
            self.delete(existing)
        self.append(anim_page)

    def get_shapes(self):
        query = "(descendant::" + "|descendant::".join(registered_shapes) + ")"
        return self.get_elements(query)

    def get_formatted_text(self, context):
        result = []
        for element in self.children:
            if element.tag == "presentation:notes":
                # No need for an advanced odf_notes.get_formatted_text()
                # because the text seems to be only contained in paragraphs
                # and frames, that we already handle
                for child in element.children:
                    result.append(child.get_formatted_text(context))
                result.append("\n")
            result.append(element.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


DrawPage._define_attribut_property()

register_element_class(DrawPage)
