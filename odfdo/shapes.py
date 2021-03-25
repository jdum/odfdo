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
#          Romain Gauthier <romain@itaapy.com>
"""Drawing classes ShapeBase, LineShape, RectangleShape, EllipseShape,
ConnectorShape and DrawGroup
"""
from .element import Element, register_element_class
from .frame import AnchorMix, ZMix, PosMix, SizeMix


class ShapeBase(Element, SizeMix, PosMix):
    """Base class for shapes"""

    _tag = "draw:shape-odfdo-notodf"
    _properties = (
        ("draw_id", "draw:id"),
        ("layer", "draw:layer"),
        ("width", "svg:width"),
        ("height", "svg:height"),
        ("pos_x", "svg:x"),
        ("pos_y", "svg:y"),
        ("presentation_class", "presentation:class"),
        ("style", "draw:style-name"),
        ("text_style", "draw:text-style-name"),
    )

    def __init__(
        self,
        style=None,
        text_style=None,
        draw_id=None,
        layer=None,
        position=None,
        size=None,
        presentation_class=None,
        **kwargs
    ):
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

    def get_formatted_text(self, context):
        result = []
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

    Return: LineShape
    """

    _tag = "draw:line"
    _properties = (
        ("x1", "svg:x1"),
        ("y1", "svg:y1"),
        ("x2", "svg:x2"),
        ("y2", "svg:y2"),
    )

    def __init__(
        self,
        style=None,
        text_style=None,
        draw_id=None,
        layer=None,
        p1=None,
        p2=None,
        **kw
    ):
        kw.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
            }
        )
        super().__init__(**kw)
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

        size -- (str, str)

        position -- (str, str)

    Return: RectangleShape
    """

    _tag = "draw:rect"
    _properties = ()

    def __init__(
        self,
        style=None,
        text_style=None,
        draw_id=None,
        layer=None,
        size=None,
        position=None,
        **kw
    ):
        kw.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "size": size,
                "position": position,
            }
        )
        super().__init__(**kw)


RectangleShape._define_attribut_property()


class EllipseShape(ShapeBase):
    """Create a ellipse shape.

    Arguments:

        style -- str

        text_style -- str

        draw_id -- str

        layer -- str

        size -- (str, str)

        position -- (str, str)

    Return: EllipseShape
    """

    _tag = "draw:ellipse"
    _properties = ()

    def __init__(
        self,
        style=None,
        text_style=None,
        draw_id=None,
        layer=None,
        size=None,
        position=None,
        **kw
    ):
        kw.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "size": size,
                "position": position,
            }
        )
        super().__init__(**kw)


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

    Return: ConnectorShape
    """

    _tag = "draw:connector"
    _properties = (
        ("start_shape", "draw:start-shape"),
        ("end_shape", "draw:end-shape"),
        ("start_glue_point", "draw:start-glue-point"),
        ("end_glue_point", "draw:end-glue-point"),
        ("x1", "svg:x1"),
        ("y1", "svg:y1"),
        ("x2", "svg:x2"),
        ("y2", "svg:y2"),
    )

    def __init__(
        self,
        style=None,
        text_style=None,
        draw_id=None,
        layer=None,
        connected_shapes=None,
        glue_points=None,
        p1=None,
        p2=None,
        **kw
    ):
        kw.update(
            {
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
            }
        )
        super().__init__(**kw)
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
    _properties = (
        ("draw_id", "draw:id"),
        ("caption_id", "draw:caption-id"),
        ("draw_class_names", "draw:class-names"),
        ("name", "draw:name"),
        ("style", "draw:style-name"),
        # ('z_index', 'draw:z-index'),
        ("presentation_class_names", "presentation:class-names"),
        ("presentation_style", "presentation:style-name"),
        ("table_end_cell", "table:end-cell-address"),
        ("table_end_x", "table:end-x"),
        ("table_end_y", "table:end-y"),
        ("table_background", "table:table-background"),
        # ('anchor_page', 'text:anchor-page-number'),
        # ('anchor_type', 'text:anchor-type'),
        ("xml_id", "xml:id"),
        ("pos_x", "svg:x"),
        ("pos_y", "svg:y"),
    )

    def __init__(
        self,
        name=None,
        draw_id=None,
        style=None,
        position=None,
        z_index=0,
        anchor_type=None,
        anchor_page=None,
        presentation_style=None,
        **kwargs
    ):
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
    s._tag for s in (LineShape, RectangleShape, EllipseShape, ConnectorShape)
]
register_element_class(LineShape)
register_element_class(RectangleShape)
register_element_class(EllipseShape)
register_element_class(ConnectorShape)
register_element_class(DrawGroup)
