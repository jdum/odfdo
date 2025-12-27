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
#          Romain Gauthier <romain@itaapy.com>
"""Drawing classes ShapeBase, LineShape, PolylineShape, RectangleShape,
EllipseShape, ConnectorShape and DrawGroup.
"""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class
from .frame import AnchorMix, PosMix, SizeMix, ZMix
from .mixin_list import ListMixin
from .svg import SvgMixin


class ShapeBase(ListMixin, AnchorMix, SvgMixin, ZMix, Element):
    """Base class for all drawing shapes.

    This class provides common properties and methods for various shapes
    like lines, rectangles, ellipses, and connectors. It integrates sizing
    functionalities through mixins.
    """

    _tag = "draw:shape-odfdo-notodf"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "draw:name"),
        PropDef("draw_id", "draw:id"),
        PropDef("layer", "draw:layer"),
        PropDef("presentation_class", "presentation:class-names"),
        PropDef("presentation_style", "presentation:style-name"),
        PropDef("style", "draw:style-name"),
        PropDef("text_style", "draw:text-style-name"),
        PropDef("caption_id", "draw:caption-id"),
        PropDef("class_names", "draw:class-names"),
        PropDef("transform", "draw:transform"),
        PropDef("z_index", "draw:z-index"),
        PropDef("end_cell_address", "table:end-cell-address"),
        PropDef("end_x", "table:end-x"),
        PropDef("end_y", "table:end-y"),
        PropDefBool("table_background", "table:table-background", False),
        PropDef("xml_id", "xml:id"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        presentation_class: str | None = None,
        presentation_style: str | None = None,
        caption_id: str | None = None,
        class_names: str | None = None,
        transform: str | None = None,
        z_index: int | None = None,
        end_cell_address: str | None = None,
        end_x: str | None = None,
        end_y: str | None = None,
        table_background: bool | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ShapeBase element.

        Args:
            name: Name of the graphical element.
            style: The style name for the shape.
            text_style: The text style name for the shape.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the shape.
            # size: The (width, height) for the shape's size.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" hat
                contains the caption.
            class_names: White-space-separated list of styles
                with the family value of graphic.
            transform: White-space or comma separated list of transform
                definitions.
            z_index: Rendering order for shapes in a document instance.
            end_cell_address: End position of the shape if it is included
                in a spreadsheet document.
            end_x: The x-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            end_y: The y-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            table_background: Wether the shape is in the table background if
                the drawing shape is included in a spreadsheet.
            anchor_type: How a drawing shape is bound to a text document.
            anchor_page: Physical page number of an anchor if the drawing
                object is bound to a page within a text document.
            xml_id: The unique XML ID.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if text_style:
                self.text_style = text_style
            if draw_id:
                self.draw_id = draw_id
            if layer:
                self.layer = layer
            if presentation_class:
                self.presentation_class = presentation_class
            if presentation_style:
                self.presentation_style = presentation_style
            if caption_id:
                self.caption_id = caption_id
            if class_names:
                self.class_names = class_names
            if transform:
                self.transform = transform
            if z_index is not None:
                self.z_index = z_index
            if end_cell_address:
                self.end_cell_address = end_cell_address
            if end_x:
                self.end_x = end_x
            if end_y:
                self.end_y = end_y
            if table_background is not None:
                self.table_background = table_background
            if anchor_type:
                self.anchor_type = anchor_type
            if anchor_page is not None:
                self.anchor_page = anchor_page
            if xml_id:
                self.xml_id = xml_id

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Return the formatted text content of the shape.

        Args:
            context: A dictionary of context variables.

        Returns:
            str: The formatted text content.
        """
        result: list[str] = []
        for child in self.children:
            result.append(child.get_formatted_text(context))
        result.append("\n")
        return "".join(result)


ShapeBase._define_attribut_property()


class LineShape(ShapeBase):
    """Represents a line shape, "draw:line".

    This shape defines a straight line between two points.
    """

    _tag = "draw:line"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("x1", "svg:x1"),
        PropDef("y1", "svg:y1"),
        PropDef("x2", "svg:x2"),
        PropDef("y2", "svg:y2"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        p1: tuple[str, str] | list[str] | None = None,
        p2: tuple[str, str] | list[str] | None = None,
        presentation_class: str | None = None,
        presentation_style: str | None = None,
        caption_id: str | None = None,
        class_names: str | None = None,
        transform: str | None = None,
        z_index: int | None = None,
        end_cell_address: str | None = None,
        end_x: str | None = None,
        end_y: str | None = None,
        table_background: bool | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a line shape "draw:line".

        Args:
            name: Name of the graphical element.
            style: The style name for the line.
            text_style: The text style name for the line.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the line.
            p1: The (x1, y1) coordinates of the starting point.
            p2: The (x2, y2) coordinates of the ending point.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" hat
                contains the caption.
            class_names: White-space-separated list of styles
                with the family value of graphic.
            transform: White-space or comma separated list of transform
                definitions.
            z_index: Rendering order for shapes in a document instance.
            end_cell_address: End position of the shape if it is included
                in a spreadsheet document.
            end_x: The x-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            end_y: The y-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            table_background: Wether the shape is in the table background if
                the drawing shape is included in a spreadsheet.
            anchor_type: How a drawing shape is bound to a text document.
            anchor_page_number: Physical page number of an anchor if the drawing
                object is bound to a page within a text document.
            xml_id: The unique XML ID.
        """
        kwargs.update(
            {
                "name": name,
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "presentation_class": presentation_class,
                "presentation_style": presentation_style,
                "caption_id": caption_id,
                "class_names": class_names,
                "transform": transform,
                "z_index": z_index,
                "end_cell_address": end_cell_address,
                "end_x": end_x,
                "end_y": end_y,
                "table_background": table_background,
                "anchor_type": anchor_type,
                "anchor_page": anchor_page,
                "xml_id": xml_id,
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


class RectangleShape(PosMix, SizeMix, ShapeBase):
    """Represents a rectangle shape, "draw:rect".

    This shape defines a rectangular area.
    """

    _tag = "draw:rect"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("corner_radius", "draw:corner-radius"),
        PropDef("rx", "svg:rx"),
        PropDef("ry", "svg:ry"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        position: tuple[str, str] | list[str] | None = None,
        size: tuple[str, str] | list[str] | None = None,
        corner_radius: str | None = None,
        rx: str | None = None,
        ry: str | None = None,
        presentation_class: str | None = None,
        presentation_style: str | None = None,
        caption_id: str | None = None,
        class_names: str | None = None,
        transform: str | None = None,
        z_index: int | None = None,
        end_cell_address: str | None = None,
        end_x: str | None = None,
        end_y: str | None = None,
        table_background: bool | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a rectangle shape "draw:rect".

        Args:
            name: Name of the graphical element.
            style: The style name for the rectangle.
            text_style: The text style name for the rectangle.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the rectangle.
            position: The (x, y) coordinates for the rectangle's position.
            size: The (width, height) values for the rectangle's size.
            corner_radius: radius of the circle used to round off the corners.
            rx: x-axis radius of the ellipse used to round off the corners.
            ry: y-axis radius of the ellipse used to round off the corners.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" hat
                contains the caption.
            class_names: White-space-separated list of styles
                with the family value of graphic.
            transform: White-space or comma separated list of transform
                definitions.
            z_index: Rendering order for shapes in a document instance.
            end_cell_address: End position of the shape if it is included
                in a spreadsheet document.
            end_x: The x-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            end_y: The y-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            table_background: Wether the shape is in the table background if
                the drawing shape is included in a spreadsheet.
            anchor_type: How a drawing shape is bound to a text document.
            anchor_page: Physical page number of an anchor if the drawing
                object is bound to a page within a text document.
            xml_id: The unique XML ID.
        """
        kwargs.update(
            {
                "name": name,
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "presentation_class": presentation_class,
                "presentation_style": presentation_style,
                "caption_id": caption_id,
                "class_names": class_names,
                "transform": transform,
                "z_index": z_index,
                "end_cell_address": end_cell_address,
                "end_x": end_x,
                "end_y": end_y,
                "table_background": table_background,
                "anchor_type": anchor_type,
                "anchor_page": anchor_page,
                "xml_id": xml_id,
            }
        )
        super().__init__(**kwargs)
        if self._do_init:
            if position:
                self.position = position
            if size:
                self.size = size
            if corner_radius:
                self.corner_radius = corner_radius
            if rx:
                self.rx = rx
            if ry:
                self.rx = ry


RectangleShape._define_attribut_property()


class PolylineShape(PosMix, SizeMix, ShapeBase):
    """Represents a polyline shape, "draw:polyline"."""

    _tag = "draw:polyline"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("points", "draw:points"),
        PropDef("view_box", "svg:viewBox"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        points: str | None = None,
        position: tuple[str, str] | list[str] | None = None,
        size: tuple[str, str] | list[str] | None = None,
        view_box: str | None = None,
        presentation_class: str | None = None,
        presentation_style: str | None = None,
        caption_id: str | None = None,
        class_names: str | None = None,
        transform: str | None = None,
        z_index: int | None = None,
        end_cell_address: str | None = None,
        end_x: str | None = None,
        end_y: str | None = None,
        table_background: bool | None = None,
        anchor_type: str | None = None,
        anchor_page: int | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a polyline shape "draw:polyline".

        Args:
            name: Name of the graphical element.
            style: The style name for the polyline.
            text_style: The text style name for the polyline.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the polyline.
            points: The coordinates of the polyline.
            position: The (x, y) coordinates for the polyline's position.
            size: The (width, height) values for the polyline's size.
            view_box: The rectangle in a local coordinates system used by the
                points.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" hat
                contains the caption.
            class_names: White-space-separated list of styles
                with the family value of graphic.
            transform: White-space or comma separated list of transform
                definitions.
            z_index: Rendering order for shapes in a document instance.
            end_cell_address: End position of the shape if it is included
                in a spreadsheet document.
            end_x: The x-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            end_y: The y-coordinate of the end position of a shape relative
                to the top-left edge of a cell.
            table_background: Wether the shape is in the table background if
                the drawing shape is included in a spreadsheet.
            anchor_type: How a drawing shape is bound to a text document.
            anchor_page_number: Physical page number of an anchor if the drawing
                object is bound to a page within a text document.
            xml_id: The unique XML ID.
        """
        kwargs.update(
            {
                "name": name,
                "style": style,
                "text_style": text_style,
                "draw_id": draw_id,
                "layer": layer,
                "presentation_class": presentation_class,
                "presentation_style": presentation_style,
                "caption_id": caption_id,
                "class_names": class_names,
                "transform": transform,
                "z_index": z_index,
                "end_cell_address": end_cell_address,
                "end_x": end_x,
                "end_y": end_y,
                "table_background": table_background,
                "anchor_type": anchor_type,
                "anchor_page": anchor_page,
                "xml_id": xml_id,
            }
        )
        super().__init__(**kwargs)
        if self._do_init:
            if points:
                self.points = points
            if position:
                self.position = position
            if size:
                self.size = size
            if view_box:
                self.view_box = view_box


PolylineShape._define_attribut_property()


class EllipseShape(PosMix, SizeMix, ShapeBase):
    """Represents an ellipse shape, "draw:ellipse".

    This shape defines an elliptical or circular area.
    """

    _tag = "draw:ellipse"
    _properties: tuple[PropDef | PropDefBool, ...] = ()

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
        """Create an ellipse shape "draw:ellipse".

        Args:
            style: The style name for the ellipse.
            text_style: The text style name for the ellipse.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the ellipse.
            position: The (x, y) coordinates for the ellipse's position.
            size: The (width, height) for the ellipse's size.
        """
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
            if position:
                self.position = position
            if size:
                self.size = size


EllipseShape._define_attribut_property()


class ConnectorShape(ShapeBase):
    """Represents a connector shape, "draw:connector".

    A connector typically links two other shapes.
    """

    _tag = "draw:connector"
    _properties: tuple[PropDef | PropDefBool, ...] = (
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
        """Create a Connector shape "draw:connector".

        Args:
            style: The style name for the connector.
            text_style: The text style name for the connector.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the connector.
            connected_shapes: A tuple of (start_shape, end_shape)
                where each shape is an `Element` with a `draw_id`.
            glue_points: A tuple of (start_glue_point, end_glue_point)
                specifying the glue points for connection.
            p1: The (x1, y1) coordinates of the starting point.
            p2: The (x2, y2) coordinates of the ending point.
        """
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


class DrawGroup(AnchorMix, ZMix, PosMix):
    """Representation of a group of drawing shapes, "draw:g".

    Warning: implementation is currently minimal.

    Drawing shapes contained by a "draw:g" element that is itself
    contained by a "draw:a" element, act as hyperlinks using the
    xlink:href attribute of the containing "draw:a" element. If the
    included drawing shapes are themselves contained within "draw:a"
    elements, then the xlink:href attributes of those "draw:a" elements
    act as the hyperlink information for the shapes they contain.
    """

    _tag = "draw:g"
    _properties: tuple[PropDef | PropDefBool, ...] = (
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
        PropDef("xml_id", "xml:id"),
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
        """Create a group of drawing shapes "draw:g".

        Args:
            name: The name of the drawing group.
            draw_id: The unique ID for the drawing group.
            style: The style name for the drawing group.
            position: The (x, y) coordinates for the group's position.
            z_index: The z-index of the group, controlling its stacking order.
            anchor_type: The anchor type of the group (e.g., 'paragraph', 'char').
            anchor_page: The page number to which the group is anchored.
            presentation_style: The presentation style name for the group.
        """
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
    s._tag
    for s in (
        ConnectorShape,
        EllipseShape,
        LineShape,
        PolylineShape,
        RectangleShape,
    )
]
register_element_class(ConnectorShape)
register_element_class(DrawGroup)
register_element_class(EllipseShape)
register_element_class(LineShape)
register_element_class(PolylineShape)
register_element_class(RectangleShape)
