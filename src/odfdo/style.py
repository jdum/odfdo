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
"""Style class for various style tags and BackgroundImage class.
"""
from __future__ import annotations

__all__ = [
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
from typing import Any

from .const import CSS3_COLORMAP, ODF_PROPERTIES
from .datatype import Boolean
from .element import (
    Element,
    PropDef,
    register_element_class,
    register_element_class_list,
)
from .image import DrawImage
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

# This mapping is not exhaustive, it only contains cases where replacing
# '_' with '-' and adding the "fo:" prefix is not enough
_PROPERTY_MAPPING = {  # text
    "display": "text:display",
    "family_generic": "style:font-family-generic",
    "font": "style:font-name",
    "outline": "style:text-outline",
    "pitch": "style:font-pitch",
    "size": "fo:font-size",
    "style": "fo:font-style",
    "underline": "style:text-underline-style",
    "weight": "fo:font-weight",
    # compliance with office suites
    "font_family": "fo:font-family",
    "font_style_name": "style:font-style-name",
    # paragraph
    "align-last": "fo:text-align-last",
    "align": "fo:text-align",
    "indent": "fo:text-indent",
    "together": "fo:keep-together",
    # frame position
    "horizontal_pos": "style:horizontal-pos",
    "horizontal_rel": "style:horizontal-rel",
    "vertical_pos": "style:vertical-pos",
    "vertical_rel": "style:vertical-rel",
    # TODO 'page-break-before': 'fo:page-break-before',
    # TODO 'page-break-after': 'fo:page-break-after',
    "shadow": "fo:text-shadow",
    # Graphic
    "fill_color": "draw:fill-color",
    "fill_image_height": "draw:fill-image-height",
    "fill_image_width": "draw:fill-image-width",
    "guide_distance": "draw:guide-distance",
    "guide_overhang": "draw:guide-overhang",
    "line_distance": "draw:line-distance",
    "stroke": "draw:stroke",
    "textarea_vertical_align": "draw:textarea-vertical-align",
}


def _map_key(key: str) -> str | None:
    if key in ODF_PROPERTIES:
        return key
    key = _PROPERTY_MAPPING.get(key, key).replace("_", "-")
    if ":" not in key:
        key = f"fo:{key}"
    if key in ODF_PROPERTIES:
        return key
    return None


def _merge_dicts(dic_base: dict, *args: dict, **kwargs: Any) -> dict:
    """Merge two or more dictionaries into a new dictionary object."""
    new_dict = dic_base.copy()
    for dic in args:
        new_dict.update(dic)
    new_dict.update(kwargs)
    return new_dict


def _expand_properties_dict(properties: dict[str, str | dict]) -> dict[str, str | dict]:
    expanded = {}
    for key in sorted(properties.keys()):
        prop_key = _map_key(key)
        if not prop_key:
            continue
        expanded[prop_key] = properties[key]
    return expanded


def _expand_properties_list(properties: list[str]) -> list[str]:
    return list(filter(None, (_map_key(key) for key in properties)))


def _make_thick_string(thick: str | float | int | None) -> str:
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
        return f"{thick/100.0:.2f}pt"
    raise ValueError("Thickness must be None for default or float value (pt)")


def _make_line_string(line: str | None) -> str:
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
    """Returns a string for style:table-cell-properties fo:border,
    with default : "0.06pt solid #000000"

        thick -- str or float or int
        line -- str
        color -- str or rgb 3-tuple, str is 'black', 'grey', ... or '#012345'

    Returns : str
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
    """Return a cell style.

    The borders arguments must be some style attribute strings or None, see the
    method 'make_table_cell_border_string' to generate them.
    If the 'border' argument as the value 'default', the default style
    "0.06pt solid #000000" is used for the 4 borders.
    If any value is used for border, it is used for the 4 borders, else any of
    the 4 borders can be specified by it's own string. If all the border,
    border_top, border_bottom, ... arguments are None, an empty border is used
    (ODF value is fo:border="none").

    Padding arguments are string specifying a length (e.g. "0.5mm")". If
    'padding' is provided, it is used for the 4 sides, else any of
    the 4 sides padding can be specified by it's own string. Default padding is
    no padding.

    Arguments:

        border -- str, style string for borders on four sides

        border_top -- str, style string for top if no 'border' argument

        border_bottom -- str, style string for bottom if no 'border' argument

        border_left -- str, style string for left if no 'border' argument

        border_right -- str, style string for right if no 'border' argument

        padding -- str, style string for padding on four sides

        padding_top -- str, style string for top if no 'padding' argument

        padding_bottom -- str, style string for bottom if no 'padding' argument

        padding_left -- str, style string for left if no 'padding' argument

        padding_right -- str, style string for right if no 'padding' argument

        background_color -- str or rgb 3-tuple, str is 'black', 'grey', ... or '#012345'

        shadow -- str, e.g. "#808080 0.176cm 0.176cm"

        color -- str or rgb 3-tuple, str is 'black', 'grey', ... or '#012345'

    Return : Style
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


class Style(Element):
    """Style class for all these tags:

    'style:style'
    'number:date-style',
    'number:number-style',
    'number:percentage-style',
    'number:time-style'
    'style:font-face',
    'style:master-page',
    'style:page-layout',
    'style:presentation-page-layout',
    'text:list-style',
    'text:outline-style',
    'style:tab-stops',
    ...
    """

    _properties: tuple[PropDef, ...] = (
        PropDef("page_layout", "style:page-layout-name", "master-page"),
        PropDef("next_style", "style:next-style-name", "master-page"),
        PropDef("name", "style:name"),
        PropDef("parent_style", "style:parent-style-name"),
        PropDef("display_name", "style:display-name"),
        PropDef("svg_font_family", "svg:font-family"),
        PropDef("font_family_generic", "style:font-family-generic"),
        PropDef("font_pitch", "style:font-pitch"),
        PropDef("text_style", "text:style-name"),
        PropDef("master_page", "style:master-page-name", "paragraph"),
        PropDef("master_page", "style:master-page-name", "paragraph"),
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

    def __init__(  # noqa: C901
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
        # For family 'master-page'
        page_layout: str | None = None,
        next_style: str | None = None,
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
        width: str | None = None,
        break_before: str | None = None,
        break_after: str | None = None,
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
        """Create a style of the given family. The name is not mandatory at this
        point but will become required when inserting in a document as a common
        style.

        The display name is the name the user sees in an office application.

        The parent_style is the name of the style this style will inherit from.

        To set properties, pass them as keyword arguments. The area properties
        apply to is optional and defaults to the family.

        Arguments:

            family -- 'paragraph', 'text', 'section', 'table', 'table-column',
                      'table-row', 'table-cell', 'table-page', 'chart',
                      'drawing-page', 'graphic', 'presentation',
                      'control', 'ruby', 'list', 'number', 'page-layout'
                      'font-face', or 'master-page'

            name -- str

            display_name -- str

            parent_style -- str

            area -- str

        'text' Properties:

            italic -- bool

            bold -- bool

        'paragraph' Properties:

            master_page -- str

        'master-page' Properties:

            page_layout -- str

            next_style -- str

        'table-cell' Properties:

            border, border_top, border_right, border_bottom, border_left -- str,
            e.g. "0.002cm solid #000000" or 'none'

            padding, padding_top, padding_right, padding_bottom, padding_left -- str,
            e.g. "0.002cm" or 'none'

            shadow -- str, e.g. "#808080 0.176cm 0.176cm"

        'table-row' Properties:

            height -- str, e.g. '5cm'

            use_optimal_height -- bool

        'table-column' Properties:

            width -- str, e.g. '5cm'

            break_before -- 'page', 'column' or 'auto'

            break_after -- 'page', 'column' or 'auto'
        """
        self._family: str | None = None
        tag_or_elem = kwargs.get("tag_or_elem", None)
        if tag_or_elem is None:
            family = to_str(family)
            if family not in FAMILY_MAPPING:
                raise ValueError(f"Unknown family value: '{family}'")
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
            # Master Page
            elif family == "master-page":
                if page_layout:
                    self.page_layout = page_layout
                if next_style:
                    self.next_style = next_style
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
            # Graphic
            elif area == "graphic":
                if min_height:
                    kwargs["fo:min-height"] = min_height
            # Every other properties
            if kwargs:
                self.set_properties(kwargs, area=area)

    @property
    def family(self) -> str | None:
        if self._family is None:
            self._family = FALSE_FAMILY_MAP_REVERSE.get(
                self.tag, self.get_attribute_string("style:family")
            )
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        self._family = family
        if family in FAMILY_ODF_STD and self.tag == "style:style":
            self.set_attribute("style:family", family)

    def __repr__(self) -> str:
        return f"<Style family={self.family} name={self.name}>"

    def __str__(self) -> str:
        return repr(self)

    def get_properties(self, area: str | None = None) -> dict[str, str | dict] | None:
        """Get the mapping of all properties of this style. By default the
        properties of the same family, e.g. a paragraph style and its
        paragraph properties. Specify the area to get the text properties of
        a paragraph style for example.

        Arguments:

            area -- str

        Return: dict
        """
        if area is None:
            area = self.family
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            return None
        properties: dict[str, str | dict] = element.attributes  # type: ignore
        # Nested properties are nested dictionaries
        for child in element.children:
            properties[child.tag] = child.attributes
        return properties

    @staticmethod
    def _update_boolean_styles(props: dict[str, str | bool]) -> None:
        strike = props.get("style:text-line-through-style", "")
        if strike == "none":
            strike = ""
        underline = props.get("style:text-underline-style", "")
        if underline == "none":
            underline = ""
        props.update(
            {
                "color": props.get("fo:color") or "",
                "background_color": props.get("fo:background-color") or "",
                "italic": props.get("fo:font-style", "") == "italic",
                "bold": props.get("fo:font-weight", "") == "bold",
                "fixed": props.get("style:font-pitch", "") == "fixed",
                "underline": bool(underline),
                "strike": bool(strike),
            }
        )

    def get_list_style_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
         - "color": str
         - "background_color": str
         - "italic": bool
         - "bold": bool
         - "fixed": bool
         - "underline": bool
         - "strike": bool

        Return: dict[str, str | bool]
        """
        return self.get_text_properties()

    def get_text_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
         - "color": str
         - "background_color": str
         - "italic": bool
         - "bold": bool
         - "fixed": bool
         - "underline": bool
         - "strike": bool

        Return: dict[str, str | bool]
        """
        props: dict[str, str | bool] = self.get_properties(area="text") or {}
        self._update_boolean_styles(props)
        return props

    def set_properties(  # noqa: C901
        self,
        properties: dict[str, str | dict] | None = None,
        style: Style | None = None,
        area: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the properties of the "area" type of this style. Properties
        are given either as a dict or as named arguments (or both). The area
        is identical to the style family by default. If the properties
        element is missing, it is created.

        Instead of properties, you can pass a style with properties of the
        same area. These will be copied.

        Arguments:

            properties -- dict

            style -- Style

            area -- 'paragraph', 'text'...
        """
        if properties is None:
            properties = {}
        if area is None:
            if isinstance(self.family, bool):
                area = None
            else:
                area = self.family
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            element = Element.from_tag(f"style:{area}-properties")
            self.append(element)
        if properties or kwargs:
            properties = _expand_properties_dict(_merge_dicts(properties, kwargs))
        elif style is not None:
            properties = style.get_properties(area=area)
            if properties is None:
                return
        if properties is None:
            return
        for key, value in properties.items():
            if value is None:
                element.del_attribute(key)
            elif isinstance(value, (str, bool, tuple)):
                element.set_attribute(key, value)
            else:
                pass

    def del_properties(
        self,
        properties: list[str] | None = None,
        area: str | None = None,
    ) -> None:
        """Delete the given properties, either by list argument or
        positional argument (or both). Remove only from the given area,
        identical to the style family by default.

        Arguments:

            properties -- list

            area -- str
        """
        if properties is None:
            properties = []
        if area is None:
            area = self.family
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            raise ValueError(
                f"properties element is inexistent for: style:{area}-properties"
            )
        for key in _expand_properties_list(properties):
            element.del_attribute(key)

    def set_background(  # noqa: C901
        self,
        color: str | None = None,
        url: str | None = None,
        position: str | None = "center",
        repeat: str | None = None,
        opacity: str | None = None,
        filter: str | None = None,  # noqa: A002
    ) -> None:
        """Set the background color of a text style, or the background color
        or image of a paragraph style or page layout.

        With no argument, remove any existing background.

        The position is one or two of 'center', 'left', 'right', 'top' or
        'bottom'.

        The repeat is 'no-repeat', 'repeat' or 'stretch'.

        The opacity is a percentage integer (not a string with the '%s' sign)

        The filter is an application-specific filter name defined elsewhere.

        Though this method is defined on the base style class, it will raise
        an error if the style type is not compatible.

        Arguments:

            color -- '#rrggbb'

            url -- str

            position -- str

            repeat -- str

            opacity -- int

            filter -- str
        """
        family = self.family
        if family not in {
            "text",
            "paragraph",
            "page-layout",
            "section",
            "table",
            "table-row",
            "table-cell",
            "graphic",
        }:
            raise TypeError("No background support for this family")
        if url is not None and family == "text":
            raise TypeError("No background image for text styles")
        properties = self.get_element(f"style:{family}-properties")
        bg_image: BackgroundImage | None = None
        if properties is not None:
            bg_image = properties.get_element("style:background-image")  # type:ignore
        # Erasing
        if color is None and url is None:
            if properties is None:
                return
            properties.del_attribute("fo:background-color")
            if bg_image is not None:
                properties.delete(bg_image)
            return
        # Add the properties if necessary
        if properties is None:
            properties = Element.from_tag(f"style:{family}-properties")
            self.append(properties)
        # Add the color...
        if color:
            properties.set_attribute("fo:background-color", color)
            if bg_image is not None:
                properties.delete(bg_image)
        # ... or the background
        elif url:
            properties.set_attribute("fo:background-color", "transparent")
            if bg_image is None:
                bg_image = Element.from_tag("style:background-image")  # type:ignore
                properties.append(bg_image)  # type:ignore
            bg_image.url = url  # type:ignore
            if position:
                bg_image.position = position  # type:ignore
            if repeat:
                bg_image.repeat = repeat  # type:ignore
            if opacity:
                bg_image.opacity = opacity  # type:ignore
            if filter:
                bg_image.filter = filter  # type:ignore

    # list-style only:

    def get_level_style(self, level: int) -> Style | None:
        if self.family != "list":
            return None
        level_styles = (
            "(text:list-level-style-number"
            "|text:list-level-style-bullet"
            "|text:list-level-style-image)"
        )
        return self._filtered_element(level_styles, 0, level=level)  # type: ignore

    def set_level_style(  # noqa: C901
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
        """
        Arguments:

            level -- int

            num_format (for number) -- int

            bullet_char (for bullet) -- str

            url (for image) -- str

            display_levels -- int

            prefix -- str

            suffix -- str

            start_value -- int

            style -- str

            clone -- List Style

        Return:
            level_style created
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

    # page-layout only:

    def get_header_style(self) -> Element | None:
        if self.family != "page-layout":
            return None
        return self.get_element("style:header-style")

    def set_header_style(self, new_style: Style) -> None:
        if self.family != "page-layout":
            return
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)

    def get_footer_style(self) -> Style | None:
        if self.family != "page-layout":
            return None
        return self.get_element("style:footer-style")  # type: ignore

    def set_footer_style(self, new_style: Style) -> None:
        if self.family != "page-layout":
            return
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)

    # master-page only:

    def _set_header_or_footer(
        self,
        text_or_element: str | Element | list[Element | str],
        name: str = "header",
        style: str = "Header",
    ) -> None:
        if name == "header":
            header_or_footer = self.get_page_header()
        else:
            header_or_footer = self.get_page_footer()
        if header_or_footer is None:
            header_or_footer = Element.from_tag("style:" + name)
            self.append(header_or_footer)
        else:
            header_or_footer.clear()
        if (
            isinstance(text_or_element, Element)
            and text_or_element.tag == f"style:{name}"
        ):
            # Already a header or footer?
            self.delete(header_or_footer)
            self.append(text_or_element)
            return
        if isinstance(text_or_element, (Element, str)):
            elem_list: list[Element | str] = [text_or_element]
        else:
            elem_list = text_or_element
        for item in elem_list:
            if isinstance(item, str):
                paragraph = Element.from_tag("text:p")
                paragraph.style = style  # type: ignore
                header_or_footer.append(paragraph)
            elif isinstance(item, Element):
                header_or_footer.append(item)

    def get_page_header(self) -> Element | None:
        """Get the element that contains the header contents.

        If None, no header was set.
        """
        if self.family != "master-page":
            return None
        return self.get_element("style:header")

    def set_page_header(
        self,
        text_or_element: str | Element | list[Element | str],
    ) -> None:
        """Create or replace the header by the given content. It can already
        be a complete header.

        If you only want to update the existing header, get it and use the
        API.

        Arguments:

            text_or_element -- str or Element or a list of them
        """
        if self.family != "master-page":
            return None
        self._set_header_or_footer(text_or_element)

    def get_page_footer(self) -> Element | None:
        """Get the element that contains the footer contents.

        If None, no footer was set.
        """
        if self.family != "master-page":
            return None
        return self.get_element("style:footer")

    def set_page_footer(
        self,
        text_or_element: str | Element | list[Element | str],
    ) -> None:
        """Create or replace the footer by the given content. It can already
        be a complete footer.

        If you only want to update the existing footer, get it and use the
        API.

        Arguments:

            text_or_element -- str or Element or a list of them
        """
        if self.family != "master-page":
            return None
        self._set_header_or_footer(text_or_element, name="footer", style="Footer")

    # font-face only:

    def set_font(
        self,
        name: str,
        family: str | None = None,
        family_generic: str | None = None,
        pitch: str = "variable",
    ) -> None:
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
    _tag = "style:background-image"
    _properties: tuple[PropDef, ...] = (
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
    ):
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


# Some predefined styles


def default_number_style() -> Element:
    return Element.from_tag(
        """<number:number-style style:name="lpod-default-number-style">
           <number:number number:decimal-places="2"
            number:min-integer-digits="1"/>
           </number:number-style>"""
    )


def default_percentage_style() -> Element:
    return Element.from_tag(
        """<number:percentage-style
            style:name="lpod-default-percentage-style">
           <number:number number:decimal-places="2"
            number:min-integer-digits="1"/>
           <number:text>%</number:text>
           </number:percentage-style>"""
    )


def default_time_style() -> Element:
    return Element.from_tag(
        """<number:time-style style:name="lpod-default-time-style">
           <number:hours number:style="long"/>
           <number:text>:</number:text>
           <number:minutes number:style="long"/>
           <number:text>:</number:text>
           <number:seconds number:style="long"/>
           </number:time-style>"""
    )


def default_date_style() -> Element:
    return Element.from_tag(
        """
           <number:date-style style:name="lpod-default-date-style">
           <number:year number:style="long"/>
           <number:text>-</number:text>
           <number:month number:style="long"/>
           <number:text>-</number:text>
           <number:day number:style="long"/>
           </number:date-style>"""
    )


def default_boolean_style() -> Element:
    return Element.from_tag(
        """<number:boolean-style style:name="lpod-default-boolean-style">
           <number:boolean/>
           </number:boolean-style>"""
    )


def default_currency_style() -> Element:
    return Element.from_tag(
        """<number:currency-style style:name="lpod-default-currency-style">
            <number:text>-</number:text>
            <number:number number:decimal-places="2"
             number:min-integer-digits="1"
             number:grouping="true"/>
            <number:text> </number:text>
            <number:currency-symbol
             number:language="fr"
             number:country="FR">€</number:currency-symbol>
           </number:currency-style>"""
    )


register_element_class(BackgroundImage)
register_element_class_list(Style, STYLES_TO_REGISTER)
