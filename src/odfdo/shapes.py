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
"""Drawing classes ShapeBase, LineShape, PolylineShape, PolygonShape,
RectangleShape, EllipseShape, ConnectorShape and DrawGroup.
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
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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


class AngleMix(Element):
    """Kind, start_angle and end_angle for circle and ellipse.

    Kind value can be: 'full', 'section', 'cut' or 'arc'. Default is 'full'.
    """

    _tag = "draw:anglemix-odfdo-notodf"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("start_angle", "draw:start-angle"),
        PropDef("end_angle", "draw:end-angle"),
    )

    KIND_VALUE_CHOICE = {  # noqa: RUF012
        "full",
        "section",
        "cut",
        "arc",
    }

    @property
    def kind(self) -> str:
        'Get or set the kind, "draw:kind".'
        return self._get_attribute_str_default("draw:kind", "full")

    @kind.setter
    def kind(self, kind: str) -> None:
        if kind not in self.KIND_VALUE_CHOICE:
            raise TypeError(f"'draw:kind' not valid: {kind!r}")
        self._set_attribute_str_default("draw:kind", kind, "full")


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
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            self.p1 = p1
            self.p2 = p2

    @property
    def p1(self) -> tuple[str | None, str | None]:
        "Get or set the (x1, y1) coordinates of the starting point."
        return (self.x1, self.y1)

    @p1.setter
    def p1(self, p1: tuple[str, str] | list[str] | None) -> None:
        if p1 is None:
            self.x1 = None
            self.y1 = None
        else:
            self.x1 = p1[0]
            self.y1 = p1[1]

    @property
    def p2(self) -> tuple[str | None, str | None]:
        "Get or set the (x2, y2) coordinates of the ending point."
        return (self.x2, self.y2)

    @p2.setter
    def p2(self, p2: tuple[str, str] | list[str] | None) -> None:
        if p2 is None:
            self.x2 = None
            self.y2 = None
        else:
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
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
                self.ry = ry


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
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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


class PolygonShape(PolylineShape):
    """Represents a polygon, "draw:polygon".

    A polygon is a closed set of straight lines."""

    _tag = "draw:polygon"

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
        """Create a polygon shape "draw:polygon>".

        Args:
            name: Name of the graphical element.
            style: The style name for the polygon.
            text_style: The text style name for the polygon.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the polygon.
            points: The coordinates of the polygon.
            position: The (x, y) coordinates for the polygon's position.
            size: The (width, height) values for the polygon's size.
            view_box: The rectangle in a local coordinates system used by the
                points.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
                "points": points,
                "position": position,
                "size": size,
                "view_box": view_box,
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


PolygonShape._define_attribut_property()


class RegularPolygonShape(PosMix, SizeMix, ShapeBase):
    """Represents a regular polygon, "draw:regular-polygon".

    A regular polygon is a polygon that is specified by its number of edges
    (that is equal to the number of its corners), rather than by arbitrary
    points."""

    _tag = "draw:regular-polygon"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDefBool("concave", "draw:concave", False),
        PropDef("sharpness", "draw:sharpness"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        corners: int | None = None,
        concave: bool | None = None,
        sharpness: str | None = None,
        position: tuple[str, str] | list[str] | None = None,
        size: tuple[str, str] | list[str] | None = None,
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
        """Create a regular polygon shape "draw:regular-polygon".

        Args:
            name: Name of the graphical element.
            style: The style name for the polygon.
            text_style: The text style name for the polygon.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the polygon.
            corners: The number of polygon corners.
            concave: Whether a regular polygon is convex or concave.
            sharpness: The radius of the ellipse on which inner polygon
                corners are located for concave polygon.
            position: The (x, y) coordinates for the polygon's position.
            size: The (width, height) values for the polygon's size.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if corners:
                self.corners = corners
            if concave is not None:
                self.concave = concave
            if sharpness:
                self.sharpness = sharpness
            if position:
                self.position = position
            if size:
                self.size = size

    @property
    def corners(self) -> int | None:
        """Get or set the number of polygon corners.

        type : int or None
        """
        corners = self.get_attribute("draw:corners")
        if corners is None:
            return None
        return int(corners)

    @corners.setter
    def corners(self, corners: int | None) -> None:
        self._set_attribute_int("draw:corners", corners)


RegularPolygonShape._define_attribut_property()


class DrawPath(PosMix, SizeMix, ShapeBase):
    """Represents a path, "draw:path".

    A path is a shape with a user-defined outline. The outline is defined by
    the svg:d attribute.
    """

    _tag = "draw:path"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("svg_d", "svg:d"),
        PropDef("view_box", "svg:viewBox"),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        svg_d: str | None = None,
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
        """Create a path shape "draw:path".

        Args:
            name: Name of the graphical element.
            style: The style name for the path.
            text_style: The text style name for the path.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the path.
            svg_d: A path data.
            position: The (x, y) coordinates for the path's position.
            size: The (width, height) values for the path's size.
            view_box: The rectangle in a local coordinates system used by the
                points.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if svg_d:
                self.svg_d = svg_d
            if position:
                self.position = position
            if size:
                self.size = size
            if view_box:
                self.view_box = view_box


DrawPath._define_attribut_property()


class EllipseShape(AngleMix, PosMix, SizeMix, ShapeBase):
    """Represents an ellipse shape, "draw:ellipse".

    This shape defines an elliptical or circular area.
    """

    _tag = "draw:ellipse"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("cx", "svg:cx"),
        PropDef("cy", "svg:cy"),
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
        kind: str | None = None,
        start_angle: str | None = None,
        end_angle: str | None = None,
        cx: str | None = None,
        cy: str | None = None,
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
        """Create an ellipse shape "draw:ellipse".

        Args:
            name: Name of the graphical element.
            style: The style name for the ellipse.
            text_style: The text style name for the ellipse.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the ellipse.
            position: The (x, y) coordinates for the ellipse's position.
            size: The (width, height) for the ellipse's size.
            kind: The appearance of a circle or ellipse, "full", "section",
                "cut" or "arc". Default is "full".
            start_angle: The start angle of a section, cut, or arc where the
                draw:kind is "section", "cut" or "arc".
            end_angle: The end angle of a section, cut, or arc where the
                draw:kind is "section", "cut" or "arc".
            cx: The x-axis coordinate of the center of a circular image map
                area.
            cy: The y-axis coordinate of the center of a circular image map
                area.
            rx: The x-axis radius of the ellipse.
            ry: The y-axis radius of the ellipse.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if kind:
                self.kind = kind
            if start_angle:
                self.start_angle = start_angle
            if end_angle:
                self.end_angle = end_angle
            if cx:
                self.cx = cx
            if cy:
                self.cy = cy
            if rx:
                self.rx = rx
            if ry:
                self.ry = ry


EllipseShape._define_attribut_property()


class CircleShape(AngleMix, PosMix, SizeMix, ShapeBase):
    """Represents an circular shape, "draw:circle".

    This shape defines a circular area.
    """

    _tag = "draw:circle"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("radius", "svg:r"),
        PropDef("cx", "svg:cx"),
        PropDef("cy", "svg:cy"),
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
        radius: str | None = None,
        kind: str | None = None,
        start_angle: str | None = None,
        end_angle: str | None = None,
        center: tuple[str, str] | list[str] | None = None,
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
        """Create a circular shape "draw:circle".

        Args:
            name: Name of the graphical element.
            style: The style name for the circle.
            text_style: The text style name for the circle.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the circle.
            position: The (x, y) coordinates for the circle's position.
            size: The (width, height) for the circle's size.
            radius: The radius of the circle.
            kind: The appearance of a circle or circle, "full", "section",
                "cut" or "arc". Default is "full".
            start_angle: The start angle of a section, cut, or arc where the
                draw:kind is "section", "cut" or "arc".
            end_angle: The end angle of a section, cut, or arc where the
                draw:kind is "section", "cut" or "arc".
            center: The x-axis coordinate of the center of a circular image map
                area.
            center: The (cx, cy) coordinates of the center of the circle.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if radius:
                self.radius = radius
            if kind:
                self.kind = kind
            if start_angle:
                self.start_angle = start_angle
            if end_angle:
                self.end_angle = end_angle
            if center:
                self.center = center

    @property
    def center(self) -> tuple[str | None, str | None]:
        "Get or set the center (cx, cy) coordinates of the circle."
        return (self.cx, self.cy)

    @center.setter
    def center(self, center: tuple[str, str] | list[str] | None) -> None:
        if center is None:
            self.cx = None
            self.cy = None
        else:
            self.cx = center[0]
            self.cy = center[1]


CircleShape._define_attribut_property()


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
        PropDef("line_skew", "draw:line-skew"),
        PropDef("svg_d", "svg:d"),
        PropDef("view_box", "svg:viewBox"),
    )

    DRAW_TYOE_CHOICE = {  # noqa: RUF012
        "standard",
        "lines",
        "line",
        "curve",
    }

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        text_style: str | None = None,
        draw_id: str | None = None,
        layer: str | None = None,
        connected_shapes: tuple[ShapeBase, ShapeBase] | list[ShapeBase] | None = None,
        glue_points: tuple[str | int, str | int] | list[str | int] | None = None,
        p1: tuple[str, str] | list[str] | None = None,
        p2: tuple[str, str] | list[str] | None = None,
        draw_type: str | None = None,
        line_skew: str | None = None,
        svg_d: str | None = None,
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
        """Create a connector shape "draw:connector".

        Args:
            name: Name of the graphical element.
            style: The style name for the connector.
            text_style: The text style name for the connector.
            draw_id: The unique ID for the drawing shape.
            layer: The drawing layer of the connector.
            connected_shapes: A tuple of (start_shape, end_shape)
                where each shape is a shape with a `draw_id`.
            glue_points: A tuple of (start_glue_point, end_glue_point)
                specifying the glue points for connection.
            p1: The (x1, y1) coordinates of the starting point.
            p2: The (x2, y2) coordinates of the ending point.
            draw_type: The line or series of lines that connect two glue
                points. Values are 'standard' (default), 'lines', 'line'
                or 'curve'.
            line_skew: A list of offsets for the placements of connector
                lines if the connector is of type standard.
            svg_d: A path data.
            view_box: The rectangle in a local coordinates system used by the
                points.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if connected_shapes:
                self.connected_shapes = connected_shapes
            if glue_points:
                self.glue_points = glue_points
            self.p1 = p1
            self.p2 = p2
            if draw_type:
                self.draw_type = draw_type
            if line_skew:
                self.line_skew = line_skew
            if svg_d:
                self.svg_d = svg_d
            if view_box:
                self.view_box = view_box

    @property
    def connected_shapes(self) -> tuple[str | None, str | None]:
        """Get or set the connected shapes ("draw:start-shape",
        "draw:end-shape")."""
        get_attr = self.get_attribute_string
        return get_attr("draw:start-shape"), get_attr("draw:end-shape")

    @connected_shapes.setter
    def connected_shapes(
        self, connected_shapes: tuple[ShapeBase, ShapeBase] | list[ShapeBase] | None
    ) -> None:
        if connected_shapes is None:
            self.start_shape = None
            self.end_shape = None
        else:
            self.start_shape = connected_shapes[0].draw_id
            self.end_shape = connected_shapes[1].draw_id

    @property
    def glue_points(self) -> tuple[str | None, str | None]:
        """Get or set the the glue points for connection
        ("draw:start-glue-point", "draw:end-glue-point")."""
        get_attr = self.get_attribute_string
        return get_attr("draw:start-glue-point"), get_attr("draw:end-glue-point")

    @glue_points.setter
    def glue_points(
        self, glue_points: tuple[str | int, str | int] | list[str | int] | None
    ) -> None:
        if glue_points is None:
            self.start_glue_point = None
            self.end_glue_point = None
        else:
            self.start_glue_point = glue_points[0]
            self.end_glue_point = glue_points[1]

    @property
    def p1(self) -> tuple[str | None, str | None]:
        "Get or set the (x1, y1) coordinates of the starting point."
        return (self.x1, self.y1)

    @p1.setter
    def p1(self, p1: tuple[str, str] | list[str] | None) -> None:
        if p1 is None:
            self.x1 = None
            self.y1 = None
        else:
            self.x1 = p1[0]
            self.y1 = p1[1]

    @property
    def p2(self) -> tuple[str | None, str | None]:
        "Get or set the (x2, y2) coordinates of the ending point."
        return (self.x2, self.y2)

    @p2.setter
    def p2(self, p2: tuple[str, str] | list[str] | None) -> None:
        if p2 is None:
            self.x2 = None
            self.y2 = None
        else:
            self.x2 = p2[0]
            self.y2 = p2[1]

    @property
    def draw_type(self) -> str:
        'Get or set the draw type, "draw:type".'
        return self._get_attribute_str_default("draw:type", "standard")

    @draw_type.setter
    def draw_type(self, draw_type: str) -> None:
        if draw_type not in self.DRAW_TYOE_CHOICE:
            raise TypeError(f"'draw:type' not valid: {draw_type!r}")
        self._set_attribute_str_default("draw:type", draw_type, "standard")


ConnectorShape._define_attribut_property()


class DrawGroup(SvgMixin, AnchorMix, ZMix, Element):
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
        PropDef("name", "draw:name"),
        PropDef("style", "draw:style-name"),
        PropDef("draw_id", "draw:id"),
        PropDef("svg_y", "svg:y"),
        PropDef("presentation_class", "presentation:class-names"),
        PropDef("presentation_style", "presentation:style-name"),
        PropDef("caption_id", "draw:caption-id"),
        PropDef("class_names", "draw:class-names"),
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
        draw_id: str | None = None,
        svg_y: str | None = None,
        presentation_class: str | None = None,
        presentation_style: str | None = None,
        caption_id: str | None = None,
        class_names: str | None = None,
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
        """Create a group of drawing shapes "draw:g".

        Args:
            name: Name of the group.
            style: The style name for the group.
            draw_id: The unique ID for the drawing group.
            svg_y: Position on the y-axis of the group.
            presentation_class: White-space-separated list of presentation
                class names.
            presentation_style: Style for a presentation shape.
            caption_id: Target ID assigned to the "draw:text-box" that
                contains the caption.
            class_names: White-space-separated list of styles with the
                family value of graphic.
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
            if draw_id:
                self.draw_id = draw_id
            if svg_y:
                self.svg_y = svg_y
            if presentation_class:
                self.presentation_class = presentation_class
            if presentation_style:
                self.presentation_style = presentation_style
            if caption_id:
                self.caption_id = caption_id
            if class_names:
                self.class_names = class_names
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


DrawGroup._define_attribut_property()

registered_shapes = [
    s._tag
    for s in (
        CircleShape,
        ConnectorShape,
        EllipseShape,
        LineShape,
        PolygonShape,
        PolylineShape,
        RectangleShape,
        RegularPolygonShape,
        DrawPath,
    )
]
register_element_class(CircleShape)
register_element_class(ConnectorShape)
register_element_class(DrawGroup)
register_element_class(DrawPath)
register_element_class(EllipseShape)
register_element_class(LineShape)
register_element_class(PolygonShape)
register_element_class(PolylineShape)
register_element_class(RectangleShape)
register_element_class(RegularPolygonShape)
