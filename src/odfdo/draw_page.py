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
"""DrawPage class for "draw:page" tag."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .office_forms import OfficeFormsMixin
from .shapes import registered_shapes
from .smil import AnimPar, AnimTransFilter


class DrawPage(OfficeFormsMixin, Element):
    """ODF draw page for presentations and drawings, "draw:page"."""

    _tag = "draw:page"
    _properties = (
        PropDef("name", "draw:name"),
        PropDef("draw_id", "draw:id"),
        PropDef("master_page", "draw:master-page-name"),
        PropDef(
            "presentation_page_layout", "presentation:presentation-page-layout-name"
        ),
        PropDef("style", "draw:style-name"),
    )

    def __init__(
        self,
        draw_id: str | None = None,
        name: str | None = None,
        master_page: str | None = None,
        presentation_page_layout: str | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the DrawPage.

        Args:
            draw_id: The ID of the draw page ('draw:id').
            name: The name of the draw page ('draw:name').
            master_page: The name of the master page to use
                ('draw:master-page-name').
            presentation_page_layout: The name of the
                presentation page layout to use
                ('presentation:presentation-page-layout-name').
            style: The name of the style to apply to the page
                ('draw:style-name').
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
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

    def get_transition(self) -> AnimPar | None:
        """Get the animation transition element for the page.

        Returns:
            AnimPar | None: The animation transition element (`anim:par`),
                or `None` if no transition is defined.
        """
        return self.get_element("anim:par")  # type: ignore

    def set_transition(
        self,
        smil_type: str,
        subtype: str | None = None,
        dur: str = "2s",
        node_type: str = "default",
    ) -> None:
        """Set or replace the animation transition for the page.

        This method creates a new animation transition (`anim:par` element)
        and replaces any existing transition on the page.

        Args:
            smil_type: The SMIL type for the transition (e.g., "fade").
            subtype: The SMIL subtype for the transition.
            dur: The duration of the transition (e.g., "2s").
            node_type: The presentation node type.
        """
        # Create the new animation
        anim_page = AnimPar(presentation_node_type=node_type)
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
        previous_transition = self.get_transition()
        if previous_transition:
            self.delete(previous_transition)
        self.append(anim_page)

    def get_shapes(self) -> list[Element]:
        """Get all shape elements within the page.

        This includes all registered shapes such as lines, rectangles,
        ellipses, and connectors.

        Returns:
            list[Element]: A list of all shape elements found on the page.
        """
        query = "(descendant::" + "|descendant::".join(registered_shapes) + ")"
        return self.get_elements(query)

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Return a formatted string representation of the page's content.

        This method recursively formats the text of all child elements,
        including presentation notes.

        Args:
            context: A dictionary providing context for formatting,
                such as footnote or annotation tracking.

        Returns:
            str: A formatted string of the page's textual content.
        """
        result: list[str] = []
        for child in self.children:
            if child.tag == "presentation:notes":
                # No need for an advanced odf_notes.get_formatted_text()
                # because the text seems to be only contained in paragraphs
                # and frames, that we already handle
                for sub_child in child.children:
                    result.append(sub_child.get_formatted_text(context))
                result.append("\n")
            result.append(child.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


DrawPage._define_attribut_property()

register_element_class(DrawPage)
