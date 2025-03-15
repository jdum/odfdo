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
# Authors: David Versmisse <david.versmisse@itaapy.com>
"""Classes for ODF implementation of SMIL (Synchronized Multimedia
Integration Language).
"""
from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


class AnimPar(Element):
    """A container for SMIL Presentation Animations.

    Arguments:

        presentation_node_type -- default, on-click, with-previous,
                                  after-previous, timing-root, main-sequence
                                  and interactive-sequence

        smil_begin -- indefinite, 10s, [id].click, [id].begin
    """

    _tag = "anim:par"
    _properties = (
        PropDef("presentation_node_type", "presentation:node-type"),
        PropDef("smil_begin", "smil:begin"),
    )

    def __init__(
        self,
        presentation_node_type: str | None = None,
        smil_begin: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            if presentation_node_type:
                self.presentation_node_type = presentation_node_type
            if smil_begin:
                self.smil_begin = smil_begin


AnimPar._define_attribut_property()


class AnimSeq(Element):
    """TA container for SMIL Presentation Animations. Animations
    inside this block are executed after the slide has executed its initial
    transition.

    Arguments:

        presentation_node_type -- default, on-click, with-previous,
                                  after-previous, timing-root, main-sequence
                                  and interactive-sequence
    """

    _tag = "anim:seq"
    _properties = (PropDef("presentation_node_type", "presentation:node-type"),)

    def __init__(
        self,
        presentation_node_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if self._do_init and presentation_node_type:
            self.presentation_node_type = presentation_node_type


AnimSeq._define_attribut_property()


class AnimTransFilter(Element):
    """
    Class to make a beautiful transition between two frames.

    Arguments:

      smil_dur -- str, duration

      smil_type and smil_subtype -- see http://www.w3.org/TR/SMIL20/
                    smil-transitions.html#TransitionEffects-Appendix
                                    to get a list of all types/subtypes

      smil_direction -- forward, reverse

      smil_fadeColor -- forward, reverse

      smil_mode -- in, out
    """

    _tag = "anim:transitionFilter"
    _properties = (
        PropDef("smil_dur", "smil:dur"),
        PropDef("smil_type", "smil:type"),
        PropDef("smil_subtype", "smil:subtype"),
        PropDef("smil_direction", "smil:direction"),
        PropDef("smil_fadeColor", "smil:fadeColor"),
        PropDef("smil_mode", "smil:mode"),
    )

    def __init__(
        self,
        smil_dur: str | None = None,
        smil_type: str | None = None,
        smil_subtype: str | None = None,
        smil_direction: str | None = None,
        smil_fadeColor: str | None = None,
        smil_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            if smil_dur:
                self.smil_dur = smil_dur
            if smil_type:
                self.smil_type = smil_type
            if smil_subtype:
                self.smil_subtype = smil_subtype
            if smil_direction:
                self.smil_direction = smil_direction
            if smil_fadeColor:
                self.smil_fadeColor = smil_fadeColor
            if smil_mode:
                self.smil_mode = smil_mode


AnimTransFilter._define_attribut_property()

register_element_class(AnimPar)
register_element_class(AnimSeq)
register_element_class(AnimTransFilter)
