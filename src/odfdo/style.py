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
"""Style class for various style tags and BackgroundImage class."""

from __future__ import annotations

from typing import Any

from .const import ODF_PROPERTIES
from .datatype import Boolean
from .element import (
    Element,
    PropDef,
    PropDefBool,
    register_element_class,
    register_element_class_list,
)
from .image import DrawImage
from .style_base import StyleBase
from .style_defaults import (
    default_boolean_style,
    default_currency_style,
    default_date_style,
    default_number_style,
    default_percentage_style,
    default_time_style,
)
from .style_props import StyleProps
from .style_utils import _set_background
from .utils import (
    FALSE_FAMILY_MAP_REVERSE,
    FAMILY_MAPPING,
    FAMILY_ODF_STD,
    STYLES_TO_REGISTER,
    SUBCLASSED_STYLES,
    hex2rgb,
    hexa_color,
    rgb2hex,
    to_str,
)
from .utils.css3_colormap import CSS3_COLORMAP

__all__ = [  # noqa: RUF022
    "BackgroundImage",
    "CSS3_COLORMAP",
    "ODF_PROPERTIES",
    "Style",
    "create_table_cell_style",
    "default_boolean_style",
    "default_currency_style",
    "default_date_style",
    "default_number_style",
    "default_percentage_style",
    "default_time_style",
    "hex2rgb",
    "make_table_cell_border_string",
    "rgb2hex",
]


def _make_thick_string(thick: str | float | int | None) -> str:
    """Helper to convert a thickness value to a string for border properties.

    Args:
        thick: The thickness value. Can be a string
            (e.g., "1pt"), a float (e.g., 0.5 for 0.5pt), or an int (e.g., 100 for 1.00pt).

    Returns:
        str: The formatted thickness string (e.g., "0.06pt").

    Raises:
        ValueError: If the thickness type is not supported.
    """
    THICK_DEFAULT = "0.06pt"
    if thick is None:
        return THICK_DEFAULT
    if isinstance(thick, str):
        thick = thick.strip()
        if thick:
            return thick
        return THICK_DEFAULT
    if isinstance(thick, float):
        return f"{thick:.2f}pt"
    if isinstance(thick, int):
        return f"{thick / 100.0:.2f}pt"
    raise ValueError("Thickness must be None for default or float value (pt)")


def _make_line_string(line: str | None) -> str:
    """Helper to convert a line style value to a string for border properties.

    Args:
        line: The line style value (e.g., "solid", "dotted").

    Returns:
        str: The formatted line style string (e.g., "solid").

    Raises:
        ValueError: If the line style type is not supported.
    """
    LINE_DEFAULT = "solid"
    if line is None:
        return LINE_DEFAULT
    if isinstance(line, str):
        line = line.strip()
        if line:
            return line
        return LINE_DEFAULT
    raise ValueError("Line style must be None for default or string")


def make_table_cell_border_string(
    thick: str | float | int | None = None,
    line: str | None = None,
    color: str | tuple | None = None,
) -> str:
    """Generate a string for "style:table-cell-properties" "fo:border".

    The default output is "0.06pt solid #000000".

    Args:
        thick: The thickness of the border. Can be
            a string (e.g., "1pt"), a float (e.g., 0.5 for 0.5pt), or an int
            (e.g., 100 for 1.00pt).
        line: The style of the line (e.g., "solid", "dotted").
        color: The color of the border. Can be a string
            (e.g., "black", "#RRGGBB") or an RGB 3-tuple.

    Returns:
        str: A formatted string suitable for the "fo:border" attribute.
    """
    thick_string = _make_thick_string(thick)
    line_string = _make_line_string(line)
    color_string = hexa_color(color) or "#000000"
    return " ".join((thick_string, line_string, color_string))


def create_table_cell_style(
    border: str | None = None,
    border_top: str | None = None,
    border_bottom: str | None = None,
    border_left: str | None = None,
    border_right: str | None = None,
    padding: str | None = None,
    padding_top: str | None = None,
    padding_bottom: str | None = None,
    padding_left: str | None = None,
    padding_right: str | None = None,
    background_color: str | tuple | None = None,
    shadow: str | None = None,
    color: str | tuple | None = None,
) -> Style:
    """Create and return a table cell style.

    The `border` arguments (e.g., `border`, `border_top`) accept style attribute
    strings (e.g., "0.06pt solid #000000") or None. Use
    `make_table_cell_border_string` to generate valid border strings.
    - If `border` is "default", the style "0.06pt solid #000000" is applied to all
      four borders.
    - If any value is provided for `border`, it overrides `border_top`, `border_bottom`, etc.
    - If all border-related arguments are None, an empty border (fo:border="none") is used.

    `padding` arguments specify a length (e.g., "0.5mm"). If `padding` is
    provided, it applies to all four sides; otherwise, individual padding
    sides can be specified. Default padding is none.

    Args:
        border: Style string for all four borders. Use "default" for a predefined style.
        border_top: Style string for the top border.
        border_bottom: Style string for the bottom border.
        border_left: Style string for the left border.
        border_right: Style string for the right border.
        padding: Style string for padding on all four sides.
        padding_top: Style string for top padding.
        padding_bottom: Style string for bottom padding.
        padding_left: Style string for left padding.
        padding_right: Style string for right padding.
        background_color: Background color (e.g., "#RRGGBB", "red", or RGB tuple).
        shadow: Shadow specification (e.g., "#808080 0.176cm 0.176cm").
        color: Text color (e.g., "black", "#RRGGBB", or RGB tuple).

    Returns:
        Style: A Style object configured for a table cell.
    """
    if border == "default":
        border = make_table_cell_border_string()  # default border
    if border is not None:
        # use the border value for 4 sides.
        border_bottom = border_top = border_left = border_right = None
    if (
        border is None
        and border_bottom is None
        and border_top is None
        and border_left is None
        and border_right is None
    ):
        border = "none"
    if padding is not None:
        # use the padding value for 4 sides.
        padding_bottom = padding_top = padding_left = padding_right = None
    cell_style = Style(
        "table-cell",
        area="table-cell",
        border=border,
        border_top=border_top,
        border_bottom=border_bottom,
        border_left=border_left,
        border_right=border_right,
        padding=padding,
        padding_top=padding_top,
        padding_bottom=padding_bottom,
        padding_left=padding_left,
        padding_right=padding_right,
        background_color=background_color,
        shadow=shadow,
    )
    if color:
        cell_style.set_properties(area="text", color=color)
    return cell_style


def _new_master_page(*args: Any, **kwargs: Any) -> StyleBase:
    """Factory function for creating a new StyleMasterPage instance.

    This function is used internally by the Style class's __new__ method
    to create StyleMasterPage objects when the 'family' is 'master-page'.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        StyleMasterPage: A new instance of StyleMasterPage.
    """
    family = kwargs.pop("family", None)
    if family is None:
        args = args[1:]
    from .master_page import StyleMasterPage

    return StyleMasterPage(*args, **kwargs)


def _new_page_layout(*args: Any, **kwargs: Any) -> StyleBase:
    """Factory function for creating a new StylePageLayout instance.

    This function is used internally by the Style class's __new__ method
    to create StylePageLayout objects when the 'family' is 'page-layout'.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        StylePageLayout: A new instance of StylePageLayout.
    """
    family = kwargs.pop("family", None)
    if family is None:
        args = args[1:]
    from .page_layout import StylePageLayout

    return StylePageLayout(*args, **kwargs)


class Style(StyleProps):
    """Represents an ODF style, "style:style", "number:date-style", etc.

    This class serves as a versatile container for various OpenDocument styles,
    providing a unified interface for managing formatting properties.

    Supported style families include:
        - "style:style"
        - "number:date-style"
        - "number:number-style"
        - "number:percentage-style"
        - "number:time-style"
        - "style:font-face"
        - "style:page-layout"
        - "style:presentation-page-layout"
        - "text:list-style"
        - "text:outline-style"
        - "style:tab-stops"
        - ... (and more)
    """

    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "style:name"),
        PropDef("parent_style", "style:parent-style-name"),
        PropDef("display_name", "style:display-name"),
        PropDef("svg_font_family", "svg:font-family"),
        PropDef("font_family_generic", "style:font-family-generic"),
        PropDef("font_pitch", "style:font-pitch"),
        PropDef("text_style", "text:style-name"),
        PropDef("master_page", "style:master-page-name", "paragraph"),
        # style:tab-stop
        PropDef("style_type", "style:type"),
        PropDef("leader_style", "style:leader-style"),
        PropDef("leader_text", "style:leader-text"),
        PropDef("style_position", "style:position"),
        PropDef("leader_text", "style:position"),
        PropDef("list_style_name", "style:list-style-name"),
        PropDef("style_num_format", "style:num-format"),
    )

    def __new__(cls, *args: Any, **kwargs: Any) -> StyleBase:  # type: ignore[misc]
        """Create a new Style instance, delegating to specialized classes for
        'master-page' or 'page-layout' families.

        Args:
            *args: Variable length argument list, potentially including the style family.
            **kwargs: Arbitrary keyword arguments, potentially including the 'family'.

        Returns:
            StyleBase: An instance of Style, StyleMasterPage, or StylePageLayout.
        """
        family = kwargs.get("family")
        if family is None and args:
            family = args[0]
        if family == "master-page":
            return _new_master_page(*args, **kwargs)
        elif family == "page-layout":
            return _new_page_layout(*args, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(
        self,
        family: str | None = None,
        name: str | None = None,
        display_name: str | None = None,
        parent_style: str | None = None,
        # Where properties apply
        area: str | None = None,
        # For family 'text':
        color: str | tuple | None = None,
        background_color: str | tuple | None = None,
        italic: bool = False,
        bold: bool = False,
        # For family 'paragraph'
        master_page: str | None = None,
        # For family 'table-cell'
        data_style: str | None = None,  # unused
        border: str | None = None,
        border_top: str | None = None,
        border_right: str | None = None,
        border_bottom: str | None = None,
        border_left: str | None = None,
        padding: str | None = None,
        padding_top: str | None = None,
        padding_bottom: str | None = None,
        padding_left: str | None = None,
        padding_right: str | None = None,
        shadow: str | None = None,
        # For family 'table-row'
        height: str | None = None,
        use_optimal_height: bool = False,
        # For family 'table-column'
        break_before: str | None = None,
        break_after: str | None = None,
        # for family 'table'
        align: str | None = None,
        # For family 'table-column' or 'table'
        width: str | None = None,
        # For family 'graphic'
        min_height: str | None = None,
        # For family 'font-face'
        font_name: str | None = None,
        font_family: str | None = None,
        font_family_generic: str | None = None,
        font_pitch: str = "variable",
        # Every other property
        **kwargs: Any,
    ) -> None:
        """Create a style of the given family.

        The name is not mandatory at this point but will become required when
        inserting in a document as a common style. The display name is the name
        the user sees in an office application. The parent_style is the name
        of the style this style will inherit from.

        To set properties, pass them as keyword arguments. The area properties
        apply to is optional and defaults to the family.

        Args:
            family: The style family. Can be 'paragraph', 'text',
                'section', 'table', 'table-column', 'table-row', 'table-cell',
                'table-page', 'chart', 'drawing-page', 'graphic', 'presentation',
                'control', 'ruby', 'list', 'number', 'page-layout', 'font-face',
                or 'master-page'.
            name: The programmatic name of the style.
            display_name: The display name of the style.
            parent_style: The name of the parent style.
            area: The specific area to which properties apply.
                Defaults to the style's family.

        'text' Properties:
            color: Text color (e.g., "#RRGGBB" or "red").
            background_color: Background color (e.g., "#RRGGBB" or "red").
            italic: If True, applies italic formatting.
            bold: If True, applies bold formatting.

        'paragraph' Properties:
            master_page: The master page to use for the paragraph.

        'table-cell' Properties:
            data_style: The data style for the cell. (unused)
            border: Style string for all four borders (e.g., "0.002cm solid #000000").
            border_top: Style string for the top border.
            border_right: Style string for the right border.
            border_bottom: Style string for the bottom border.
            border_left: Style string for the left border.
            padding: Style string for padding on all four sides (e.g., "0.002cm").
            padding_top: Style string for top padding.
            padding_bottom: Style string for bottom padding.
            padding_left: Style string for left padding.
            padding_right: Style string for right padding.
            shadow: Shadow specification (e.g., "#808080 0.176cm 0.176cm").

        'table-row' Properties:
            height: Row height (e.g., '5cm').
            use_optimal_height: If True, use optimal row height.

        'table-column' Properties:
            width: Column width (e.g., '5cm').
            break_before: Page or column break before ('page', 'column', or 'auto').
            break_after: Page or column break after ('page', 'column', or 'auto').

        'table' Properties:
            width: Table width (e.g., '5cm').
            align: Table alignment ('left', 'center', 'margins', or 'right').

        'graphic' Properties:
            min_height: Minimum height for the graphic (e.g., '1cm').

        'font-face' Properties:
            font_name: The font name.
            font_family: The font family.
            font_family_generic: Generic font family.
            font_pitch: Font pitch ('variable' or 'fixed'). Defaults to 'variable'.

        **kwargs: Additional properties to set on the style.
        """
        self._family: str | None = None
        tag_or_elem = kwargs.get("tag_or_elem")
        if tag_or_elem is None:
            family = to_str(family)
            if family in {"master-page", "page-layout"}:
                raise TypeError(f"Wrong initializer for: {family!r}")
            if family not in FAMILY_MAPPING:
                raise ValueError(f"Unknown family value: {family!r}")
            kwargs["tag"] = FAMILY_MAPPING[family]
        super().__init__(**kwargs)
        if self._do_init and family not in SUBCLASSED_STYLES:
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            self.family = family  # relevant test made by property
            # Common attributes
            if name:
                self.name = name
            if display_name:
                self.display_name = display_name
            if parent_style:
                self.parent_style = parent_style
            # Paragraph
            if family == "paragraph":
                if master_page:
                    self.master_page = master_page
            # Font face
            elif family == "font-face":
                if not font_name:
                    raise ValueError("A font_name is required for 'font-face' style")
                self.set_font(
                    font_name,
                    family=font_family,
                    family_generic=font_family_generic,
                    pitch=font_pitch,
                )
            # Properties
            if area is None:
                area = family
            area = to_str(area)
            # Text
            if area == "text":
                if color:
                    kwargs["fo:color"] = color
                if background_color:
                    kwargs["fo:background-color"] = background_color
                if italic:
                    kwargs["fo:font-style"] = "italic"
                    kwargs["style:font-style-asian"] = "italic"
                    kwargs["style:font-style-complex"] = "italic"
                if bold:
                    kwargs["fo:font-weight"] = "bold"
                    kwargs["style:font-weight-asian"] = "bold"
                    kwargs["style:font-weight-complex"] = "bold"
            # Table cell
            elif area == "table-cell":
                if border:
                    kwargs["fo:border"] = border
                elif border_top or border_right or border_bottom or border_left:
                    kwargs["fo:border-top"] = border_top or "none"
                    kwargs["fo:border-right"] = border_right or "none"
                    kwargs["fo:border-bottom"] = border_bottom or "none"
                    kwargs["fo:border-left"] = border_left or "none"
                else:  # no border_top, ... neither border are defined
                    pass  # left untouched
                if padding:
                    kwargs["fo:padding"] = padding
                elif padding_top or padding_right or padding_bottom or padding_left:
                    kwargs["fo:padding-top"] = padding_top or "none"
                    kwargs["fo:padding-right"] = padding_right or "none"
                    kwargs["fo:padding-bottom"] = padding_bottom or "none"
                    kwargs["fo:padding-left"] = padding_left or "none"
                else:  # no border_top, ... neither border are defined
                    pass  # left untouched
                if shadow:
                    kwargs["style:shadow"] = shadow
                if background_color:
                    kwargs["fo:background-color"] = background_color
            # Table row
            elif area == "table-row":
                if height:
                    kwargs["style:row-height"] = height
                if use_optimal_height:
                    kwargs["style:use-optimal-row-height"] = Boolean.encode(
                        use_optimal_height
                    )
                if background_color:
                    kwargs["fo:background-color"] = background_color
            # Table column
            elif area == "table-column":
                if width:
                    kwargs["style:column-width"] = width
                if break_before:
                    kwargs["fo:break-before"] = break_before
                if break_after:
                    kwargs["fo:break-after"] = break_after
            # Table
            elif area == "table":
                if width:
                    kwargs["style:width"] = width
                if align:
                    if align not in {"center", "left", "margins", "right"}:
                        raise ValueError(f"Invalid align value: {align!r}")
                    kwargs["table:align"] = align
            # Graphic
            elif area == "graphic":
                if min_height:
                    kwargs["fo:min-height"] = min_height
            # Every other properties
            if kwargs:
                self.set_properties(kwargs, area=area)

    @property
    def family(self) -> str | None:
        """Get the style family.

        Returns:
            str or None: The style family as a string, or None if not set.
        """
        if self._family is None:
            self._family = FALSE_FAMILY_MAP_REVERSE.get(
                self.tag, self.get_attribute_string("style:family")
            )
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        """Set the style family.

        Args:
            family: The style family to set.
        """
        self._family = family
        if family in FAMILY_ODF_STD and self.tag == "style:style":
            self.set_attribute("style:family", family)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family} name={self.name}>"

    def set_background(
        self,
        color: str | None = None,
        url: str | None = None,
        position: str | None = "center",
        repeat: str | None = None,
        opacity: str | int | None = None,
        filter: str | None = None,  # noqa: A002
    ) -> None:
        """Set the background color or image for the style.

        With no arguments, any existing background is removed.

        The `position` attribute can be "left", "center", "right", "top", "bottom",
        or two whitespace-separated values (e.g., "left top"). One value must be
        from {"left", "center", "right"} and the other from {"top", "center", "bottom"}.
        The default value for this attribute is "center".

        The `repeat` value can be 'no-repeat', 'repeat', or 'stretch'.

        The `opacity` is an integer percentage (0-100), not a string with a '%' sign.

        The `filter` is an application-specific filter name defined elsewhere.

        Note: This method will raise an error if the style type is not compatible
        with background properties.

        Args:
            color: The background color (e.g., '#rrggbb').
            url: The URL of the background image.
            position: The position of the background image. Defaults to "center".
            repeat: How the background image is repeated.
            opacity: The opacity of the background.
            filter: An application-specific filter name.
        """
        _set_background(self, color, url, position, repeat, opacity, filter)

    # list-style only:

    def get_level_style(self, level: int) -> Style | None:
        """Get the list level style for a specific level.

        This method is applicable only if the style family is 'list'.

        Args:
            level: The list level (1-based index).

        Returns:
            Style | None: The Style element for the specified level, or None
            if the style family is not 'list' or the level style is not found.
        """
        if self.family != "list":
            return None
        level_styles = (
            "(text:list-level-style-number"
            "|text:list-level-style-bullet"
            "|text:list-level-style-image)"
        )
        return self._filtered_element(level_styles, 0, level=level)  # type: ignore

    def set_level_style(
        self,
        level: int,
        num_format: str | None = None,
        bullet_char: str | None = None,
        url: str | None = None,
        display_levels: int | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        start_value: int | None = None,
        style: str | None = None,
        clone: Style | None = None,
    ) -> Style | None:
        """Set the list level style for a specific level.

        This method is applicable only if the style family is 'list'.

        Args:
            level: The list level to configure (1-based index).
            num_format: Number format for numbered lists.
            bullet_char: Bullet character for bulleted lists.
            url: URL of the image for image bulleted lists.
            display_levels: The number of list levels to display.
            prefix: Text prefix for the list item.
            suffix: Text suffix for the list item.
            start_value: The starting value for a numbered list.
            style: The text style name for the list item.
            clone: An existing Style object to clone properties from.

        Returns:
            Style | None: The created or modified level style, or None
            if the style family is not 'list'.

        Raises:
            ValueError: If an unknown level style type is provided.
        """
        if self.family != "list":
            return None
        # Expected name
        if num_format is not None:
            level_style_name = "text:list-level-style-number"
        elif bullet_char is not None:
            level_style_name = "text:list-level-style-bullet"
        elif url is not None:
            level_style_name = "text:list-level-style-image"
        elif clone is not None:
            level_style_name = clone.tag
        else:
            raise ValueError("unknown level style type")
        was_created = False
        # Cloning or reusing an existing element
        level_style: Style | None = None
        if clone is not None:
            level_style = clone.clone  # type: ignore
            was_created = True
        else:
            level_style = self.get_level_style(level)
            if level_style is None:
                level_style = Element.from_tag(level_style_name)  # type: ignore
                was_created = True
        if level_style is None:
            return None
        # Transmute if the type changed
        if level_style.tag != level_style_name:
            print("Warn: different style", level_style_name, level_style.tag)
            level_style.tag = level_style_name
        # Set the level
        level_style.set_attribute("text:level", str(level))
        # Set the main attribute
        if num_format is not None:
            level_style.set_attribute("fo:num-format", num_format)
        elif bullet_char is not None:
            level_style.set_attribute("text:bullet-char", bullet_char)
        elif url is not None:
            level_style.set_attribute("xlink:href", url)
        # Set attributes
        if prefix:
            level_style.set_attribute("style:num-prefix", prefix)
        if suffix:
            level_style.set_attribute("style:num-suffix", suffix)
        if display_levels:
            level_style.set_attribute("text:display-levels", str(display_levels))
        if start_value:
            level_style.set_attribute("text:start-value", str(start_value))
        if style:
            level_style.text_style = style  # type: ignore
        # Commit the creation
        if was_created:
            self.append(level_style)
        return level_style

    # font-face only:

    def set_font(
        self,
        name: str,
        family: str | None = None,
        family_generic: str | None = None,
        pitch: str = "variable",
    ) -> None:
        """Set font properties for a 'font-face' style.

        This method is applicable only if the style family is 'font-face'.

        Args:
            name: The font name.
            family: The font family. If None, defaults to `name`.
            family_generic: The generic font family (e.g., 'swiss', 'roman').
            pitch: The font pitch ('variable' or 'fixed'). Defaults to 'variable'.
        """
        if self.family != "font-face":
            return
        self.name = name
        if family is None:
            family = name
        self.svg_font_family = f'"{family}"'
        if family_generic is not None:
            self.font_family_generic = family_generic
        self.font_pitch = pitch


Style._define_attribut_property()


class BackgroundImage(Style, DrawImage):
    """Style for a background image, "style:background-image".

    This class combines styling capabilities with image-specific properties
    to manage background images within ODF documents.
    """

    _tag = "style:background-image"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "style:name"),
        PropDef("display_name", "style:display-name"),
        PropDef("svg_font_family", "svg:font-family"),
        PropDef("font_family_generic", "style:font-family-generic"),
        PropDef("font_pitch", "style:font-pitch"),
        PropDef("position", "style:position", "background-image"),
        PropDef("repeat", "style:repeat", "background-image"),
        PropDef("opacity", "draw:opacity", "background-image"),
        PropDef("filter", "style:filter-name", "background-image"),
        PropDef("text_style", "text:style-name"),
    )

    def __init__(
        self,
        name: str | None = None,
        display_name: str | None = None,
        position: str | None = None,
        repeat: str | None = None,
        opacity: str | None = None,
        filter: str | None = None,  # noqa: A002
        # Every other property
        **kwargs: Any,
    ) -> None:
        """Create a style for a background image "style:background-image".

        Args:
            name: The name of the background image style.
            display_name: The display name of the background image style.
            position: The position of the background image.
            repeat: How the background image is repeated.
            opacity: The opacity of the background image.
            filter: A filter to apply to the image.
            **kwargs: Additional properties to set on the background image style.
        """
        kwargs["family"] = "background-image"
        super().__init__(**kwargs)
        if self._do_init:
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            self.family = "background-image"
            if name:
                self.name = name
            if display_name:
                self.display_name = display_name
            if position:
                self.position = position
            if repeat:
                self.position = repeat
            if opacity:
                self.position = opacity
            if filter:
                self.position = filter
            # Every other properties
            for prop in BackgroundImage._properties:
                if prop.name in kwargs:
                    self.set_style_attribute(prop.attr, kwargs[prop.name])


BackgroundImage._define_attribut_property()


register_element_class(BackgroundImage)
register_element_class_list(Style, STYLES_TO_REGISTER)
