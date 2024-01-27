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
#          Romain Gauthier <romain@itaapy.com>
"""Drawing classes ShapeBase, LineShape, RectangleShape, EllipseShape,
ConnectorShape and DrawGroup.
"""
from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class
from .frame import AnchorMix, PosMix, SizeMix, ZMix


class ShapeBase(Element, SizeMix, PosMix):
    """Base class for shapes"""

    _tag = "draw:shape-odfdo-notodf"
    _properties: tuple[PropDef, ...] = (
        PropDef("draw_id", "draw:id"),
        PropDef("layer", "draw:layer"),
        PropDef("width", "svg:width"),
        PropDef("height", "svg:height"),
        PropDef("pos_x", "svg:x"),
        PropDef("pos_y", "svg:y"),
        PropDef("presentation_class", "presentation:class"),
        PropDef("style", "draw:style-name"),
        PropDef("text_style", "draw:text-style-name"),
    )

    def __init__(
        self,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        position: tuple | None = None,
        size: tuple | None = None,
        presentation_class: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            if style:
                self.style = style
            if text_style:
                self.text_style = text_style
            if draw_id:
                self.draw_id = draw_id
            if layer:
                self.layer = layer
            if position:
                self.position = position
            if size:
                self.size = size
            if presentation_class:
                self.presentation_class = presentation_class

    def get_formatted_text(self, context: dict | None = None) -> str:
        result: list[str] = []
        for child in self.children:
            result.append(child.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


ShapeBase._define_attribut_property()


class LineShape(ShapeBase):
    """Create a line shape.

    Arguments:

        style -- str

        text_style -- str

        draw_id -- str

        layer -- str

        p1 -- (str, str)

        p2 -- (str, str)
    """

    _tag = "draw:line"
    _properties: tuple[PropDef, ...] = (
        PropDef("x1", "svg:x1"),
        PropDef("y1", "svg:y1"),
        PropDef("x2", "svg:x2"),
        PropDef("y2", "svg:y2"),
    )

    def __init__(
        self,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        p1: tuple | None = None,
        p2: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
            }
        )
        super().__init__(**kwargs)
        if self._do_init:
            if p1:
                self.x1 = p1[0]
                self.y1 = p1[1]
            if p2:
                self.x2 = p2[0]
                self.y2 = p2[1]


LineShape._define_attribut_property()


class RectangleShape(ShapeBase):
    """Create a rectangle shape.

    Arguments:

        style -- str

        text_style -- str

        draw_id -- str

        layer -- str

        position -- (str, str)

        size -- (str, str)

    """

    _tag = "draw:rect"
    _properties: tuple[PropDef, ...] = ()

    def __init__(
        self,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        position: tuple | None = None,
        size: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "size": size,
                "position": position,
            }
        )
        super().__init__(**kwargs)


RectangleShape._define_attribut_property()


class EllipseShape(ShapeBase):
    """Create a ellipse shape.

    Arguments:

        style -- str

        text_style -- str

        draw_id -- str

        layer -- str

        position -- (str, str)

        size -- (str, str)

    """

    _tag = "draw:ellipse"
    _properties: tuple[PropDef, ...] = ()

    def __init__(
        self,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        position: tuple | None = None,
        size: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "size": size,
                "position": position,
            }
        )
        super().__init__(**kwargs)


EllipseShape._define_attribut_property()


class ConnectorShape(ShapeBase):
    """Create a Connector shape.

    Arguments:

        style -- str

        text_style -- str

        draw_id -- str

        layer -- str

        connected_shapes -- (shape, shape)

        glue_points -- (point, point)

        p1 -- (str, str)

        p2 -- (str, str)
    """

    _tag = "draw:connector"
    _properties: tuple[PropDef, ...] = (
        PropDef("start_shape", "draw:start-shape"),
        PropDef("end_shape", "draw:end-shape"),
        PropDef("start_glue_point", "draw:start-glue-point"),
        PropDef("end_glue_point", "draw:end-glue-point"),
        PropDef("x1", "svg:x1"),
        PropDef("y1", "svg:y1"),
        PropDef("x2", "svg:x2"),
        PropDef("y2", "svg:y2"),
    )

    def __init__(
        self,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        connected_shapes: tuple | None = None,
        glue_points: tuple | None = None,
        p1: tuple | None = None,
        p2: tuple | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
            }
        )
        super().__init__(**kwargs)
        if self._do_init:
            if connected_shapes:
                self.start_shape = connected_shapes[0].draw_id
                self.end_shape = connected_shapes[1].draw_id
            if glue_points:
                self.start_glue_point = glue_points[0]
                self.end_glue_point = glue_points[1]
            if p1:
                self.x1 = p1[0]
                self.y1 = p1[1]
            if p2:
                self.x2 = p2[0]
                self.y2 = p2[1]


ConnectorShape._define_attribut_property()


class DrawGroup(Element, AnchorMix, ZMix, PosMix):
    """The DrawGroup "draw:g" element represents a group of drawing shapes.

    Warning: implementation is currently minimal.

    Drawing shapes contained by a "draw:g" element that is itself
    contained by a "draw:a" element, act as hyperlinks using the
    xlink:href attribute of the containing "draw:a" element. If the
    included drawing shapes are themselves contained within "draw:a"
    elements, then the xlink:href attributes of those "draw:a" elements
    act as the hyperlink information for the shapes they contain.

    The "draw:g" element has the following attributes: draw:caption-id,
    draw:class-names, draw:id, draw:name, draw:style-name, draw:z-index,
    presentation:class-names, presentation:style-name, svg:y,
    table:end-cell-address, table:end-x, table:end-y,
    table:table-background, text:anchor-page-number, text:anchor-type,
    and xml:id.

    The "draw:g" element has the following child elements: "dr3d:scene",
    "draw:a", "draw:caption", "draw:circle", "draw:connector",
    "draw:control", "draw:custom-shape", "draw:ellipse", "draw:frame",
    "draw:g", "draw:glue-point", "draw:line", "draw:measure",
    "draw:page-thumbnail", "draw:path", "draw:polygon", "draw:polyline",
    "draw:rect", "draw:regular-polygon", "office:event-listeners",
    "svg:desc" and "svg:title".
    """

    _tag = "draw:g"
    _properties: tuple[PropDef, ...] = (
        PropDef("draw_id", "draw:id"),
        PropDef("caption_id", "draw:caption-id"),
        PropDef("draw_class_names", "draw:class-names"),
        PropDef("name", "draw:name"),
        PropDef("style", "draw:style-name"),
        # ('z_index', 'draw:z-index'),
        PropDef("presentation_class_names", "presentation:class-names"),
        PropDef("presentation_style", "presentation:style-name"),
        PropDef("table_end_cell", "table:end-cell-address"),
        PropDef("table_end_x", "table:end-x"),
        PropDef("table_end_y", "table:end-y"),
        PropDef("table_background", "table:table-background"),
        # ('anchor_page', 'text:anchor-page-number'),
        # ('anchor_type', 'text:anchor-type'),
        PropDef("xml_id", "xml:id"),
        PropDef("pos_x", "svg:x"),
        PropDef("pos_y", "svg:y"),
    )

    def __init__(
        self,
        name: str | None = None,
        draw_id: str | None = None,
        style: str | None = None,
        position: tuple | None = None,
        z_index: int = 0,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        presentation_style: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            if z_index is not None:
                self.z_index = z_index
            if name:
                self.name = name
            if draw_id is not None:
                self.draw_id = draw_id
            if style is not None:
                self.style = style
            if position is not None:
                self.position = position
            if anchor_type:
                self.anchor_type = anchor_type
            if anchor_page is not None:
                self.anchor_page = anchor_page
            if presentation_style is not None:
                self.presentation_style = presentation_style


DrawGroup._define_attribut_property()

registered_shapes = [
    s._tag for s in (LineShape, RectangleShape, EllipseShape, ConnectorShape)  # type: ignore
]
register_element_class(LineShape)
register_element_class(RectangleShape)
register_element_class(EllipseShape)
register_element_class(ConnectorShape)
register_element_class(DrawGroup)
