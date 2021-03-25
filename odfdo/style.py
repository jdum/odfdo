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
"""Style class for various style tags and BackgroundImage class
"""
from .datatype import Boolean
from .const import CSS3_COLORMAP
from .element import register_element_class, Element

from .image import DrawImage
from .utils import (
    _expand_properties,
    _merge_dicts,
    _get_element,
    isiterable,
    to_str,
    FALSE_FAMILY_MAP_REVERSE,
    FAMILY_ODF_STD,
    FAMILY_MAPPING,
    SUBCLASSED_STYLES,
    STYLES_TO_REGISTER,
)
from .paragraph import Paragraph


def hex2rgb(color):
    """Turns a "#RRGGBB" hexadecimal color representation into a (R, G, B)
    tuple.
    Arguments:

        color -- str

    Return: tuple
    """
    code = color[1:]
    if not (len(color) == 7 and color[0] == "#" and code.isalnum()):
        raise ValueError('"%s" is not a valid color' % color)
    red = int(code[:2], 16)
    green = int(code[2:4], 16)
    blue = int(code[4:6], 16)
    return (red, green, blue)


def rgb2hex(color):
    """Turns a color name or a (R, G, B) color tuple into a "#RRGGBB"
    hexadecimal representation.
    Arguments:

        color -- str or tuple

    Return: str

    Examples::

        >>> rgb2hex('yellow')
        '#FFFF00'
        >>> rgb2hex((238, 130, 238))
        '#EE82EE'
    """
    if isinstance(color, str):
        try:
            code = CSS3_COLORMAP[color.lower()]
        except KeyError:
            raise KeyError('color "%s" is unknown' % color)
    elif isinstance(color, tuple):
        if len(color) != 3:
            raise ValueError("color must be a 3-tuple")
        code = color
    else:
        raise TypeError("invalid color")
    for channel in code:
        if channel < 0 or channel > 255:
            raise ValueError("color code must be between 0 and 255")
    return "#%02X%02X%02X" % code


def __make_color_string(color=None):
    color_default = "#000000"
    if not color:
        return color_default
    if isinstance(color, tuple):
        return rgb2hex(color)
    color = to_str(color)
    msg = "Color must be None for default or color string, or RGB tuple"
    if not isinstance(color, str):
        raise ValueError(msg)
    color = color.strip()
    if not color:
        return color_default
    if color.startswith("#"):
        return color
    return rgb2hex(color)


def __make_thick_string(thick):
    thick_default = "0.06pt"
    if thick is None:
        return thick_default
    if isinstance(thick, bytes):
        thick = to_str(thick)
    if isinstance(thick, str):
        thick = thick.strip()
        if thick:
            return thick
        return thick_default
    if isinstance(thick, float):
        return "%.2fpt" % thick
    if isinstance(thick, int):
        return "%.2fpt" % (thick / 100.0)
    raise ValueError("Thickness must be None for default or float value (pt)")


def __make_line_string(line):
    line_default = "solid"
    if line is None:
        return line_default
    if isinstance(line, bytes):
        line = to_str(line)
    if isinstance(line, str):
        line = line.strip()
        if line:
            return line
        return line_default
    raise ValueError("Line style must be None for default or string")


def make_table_cell_border_string(thick=None, line=None, color=None):
    """Returns a string for style:table-cell-properties fo:border,
    with default : "0.06pt solid #000000"

        thick -- str or float
        line -- str
        color -- str or rgb 3-tuple, str is 'black', 'grey', ... or '#012345'

    Returns : str
    """
    thick_string = __make_thick_string(thick)
    line_string = __make_line_string(line)
    color_string = __make_color_string(color)
    return " ".join((thick_string, line_string, color_string))


def create_table_cell_style(
    border=None,
    border_top=None,
    border_bottom=None,
    border_left=None,
    border_right=None,
    padding=None,
    padding_top=None,
    padding_bottom=None,
    padding_left=None,
    padding_right=None,
    background_color=None,
    shadow=None,
    color=None,
):
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
    if color:
        color_string = __make_color_string(color)
    if background_color:
        bgcolor_string = __make_color_string(background_color)
    else:
        bgcolor_string = None
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
        background_color=bgcolor_string,
        shadow=shadow,
    )
    if color:
        cell_style.set_properties(area="text", color=color_string)
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

    _properties = (
        ("page_layout", "style:page-layout-name", "master-page"),
        ("next_style", "style:next-style-name", "master-page"),
        ("name", "style:name", None),
        ("parent_style", "style:parent-style-name", None),
        ("display_name", "style:display-name", None),
        ("svg_font_family", "svg:font-family", None),
        ("font_family_generic", "style:font-family-generic", None),
        ("font_pitch", "style:font-pitch", None),
        ("text_style", "text:style-name", None),
        ("master_page", "style:master-page-name", "paragraph"),
        ("master_page", "style:master-page-name", "paragraph"),
        ("master_page", "style:master-page-name", "paragraph"),
        # style:tab-stop
        ("style_type", "style:type", None),
        ("leader_style", "style:leader-style", None),
        ("leader_text", "style:leader-text", None),
        ("style_position", "style:position", None),
        ("leader_text", "style:position", None),
    )

    def __init__(
        self,
        family=None,
        name=None,
        display_name=None,
        parent_style=None,
        # Where properties apply
        area=None,
        # For family 'text':
        color=None,
        background_color=None,
        italic=False,
        bold=False,
        # For family 'paragraph'
        master_page=None,
        # For family 'master-page'
        page_layout=None,
        next_style=None,
        # For family 'table-cell'
        data_style=None,  # unused
        border=None,
        border_top=None,
        border_right=None,
        border_bottom=None,
        border_left=None,
        padding=None,
        padding_top=None,
        padding_bottom=None,
        padding_left=None,
        padding_right=None,
        shadow=None,
        # For family 'table-row'
        height=None,
        use_optimal_height=None,
        # For family 'table-column'
        width=None,
        break_before=None,
        break_after=None,
        # For family 'graphic'
        min_height=None,
        # For family 'font-face'
        font_name=None,
        font_family=None,
        font_family_generic=None,
        font_pitch="variable",
        # Every other property
        **kw,
    ):
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

        Return: Style
        """
        tag_or_elem = kw.get("tag_or_elem", None)
        if tag_or_elem is None:
            family = to_str(family)
            if family not in FAMILY_MAPPING:
                raise ValueError("Unknown family value: %s" % family)
            kw["tag"] = FAMILY_MAPPING[family]
        super().__init__(**kw)
        if self._do_init and family not in SUBCLASSED_STYLES:
            kw.pop("tag", None)
            kw.pop("tag_or_elem", None)
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
                    kw["fo:color"] = color
                if background_color:
                    kw["fo:background-color"] = background_color
                if italic:
                    kw["fo:font-style"] = "italic"
                    kw["style:font-style-asian"] = "italic"
                    kw["style:font-style-complex"] = "italic"
                if bold:
                    kw["fo:font-weight"] = "bold"
                    kw["style:font-weight-asian"] = "bold"
                    kw["style:font-weight-complex"] = "bold"
            # Table cell
            elif area == "table-cell":
                if border:
                    kw["fo:border"] = border
                elif border_top or border_right or border_bottom or border_left:
                    kw["fo:border-top"] = border_top or "none"
                    kw["fo:border-right"] = border_right or "none"
                    kw["fo:border-bottom"] = border_bottom or "none"
                    kw["fo:border-left"] = border_left or "none"
                else:  # no border_top, ... neither border are defined
                    pass  # left untouched
                if padding:
                    kw["fo:padding"] = padding
                elif padding_top or padding_right or padding_bottom or padding_left:
                    kw["fo:padding-top"] = padding_top or "none"
                    kw["fo:padding-right"] = padding_right or "none"
                    kw["fo:padding-bottom"] = padding_bottom or "none"
                    kw["fo:padding-left"] = padding_left or "none"
                else:  # no border_top, ... neither border are defined
                    pass  # left untouched
                if shadow:
                    kw["style:shadow"] = shadow
                if background_color:
                    kw["fo:background-color"] = background_color
            # Table row
            elif area == "table-row":
                if height:
                    kw["style:row-height"] = height
                if use_optimal_height is not None:
                    kw["style:use-optimal-row-height"] = Boolean.encode(
                        use_optimal_height
                    )
                if background_color:
                    kw["fo:background-color"] = background_color
            # Table column
            elif area == "table-column":
                if width:
                    kw["style:column-width"] = width
                if break_before:
                    kw["fo:break-before"] = break_before
                if break_after:
                    kw["fo:break-after"] = break_after
            # Graphic
            elif area == "graphic":
                if min_height:
                    kw["fo:min-height"] = min_height
            # Every other properties
            if kw:
                self.set_properties(kw, area=area)

    @property
    def family(self):
        try:
            return self._family
        except AttributeError:
            self._family = FALSE_FAMILY_MAP_REVERSE.get(
                self.tag, self.get_attribute("style:family")
            )
            return self._family

    @family.setter
    def family(self, family):
        family = to_str(family)
        self._family = family
        if family in FAMILY_ODF_STD and self.tag == "style:style":
            self.set_attribute("style:family", family)

    def get_properties(self, area=None):
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
        element = self.get_element("style:%s-properties" % area)
        if element is None:
            return None
        properties = element.attributes
        # Nested properties are nested dictionaries
        for child in element.children:
            properties[child.tag] = child.attributes
        return properties

    def set_properties(self, properties=None, style=None, area=None, **kw):
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
            area = self.family
        element = self.get_element("style:%s-properties" % area)
        if element is None:
            element = Element.from_tag("style:%s-properties" % area)
            self.append(element)
        if properties or kw:
            properties = _expand_properties(_merge_dicts(properties, kw))
        elif style is not None:
            properties = style.get_properties(area=area)
            if properties is None:
                return
        for key, value in properties.items():
            if value is None:
                element.del_attribute(key)
            else:
                element.set_attribute(key, value)

    def del_properties(self, properties=None, area=None):
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
        element = self.get_element("style:%s-properties" % area)
        if element is None:
            raise ValueError("properties element is inexistent")
        for key in _expand_properties(properties):
            element.del_attribute(key)

    def set_background(
        self,
        color=None,
        url=None,
        position="center",
        repeat=None,
        opacity=None,
        filter=None,
    ):
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
            raise TypeError("no background support for this family")
        if url is not None and family == "text":
            raise TypeError("no background image for text styles")
        properties = self.get_element("style:%s-properties" % family)
        if properties is None:
            bg_image = None
        else:
            bg_image = properties.get_element("style:background-image")
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
            properties = Element.from_tag("style:%s-properties" % family)
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
                bg_image = Element.from_tag("style:background-image")
                properties.append(bg_image)
            bg_image.url = url
            if position:
                bg_image.position = position
            if repeat:
                bg_image.repeat = repeat
            if opacity:
                bg_image.opacity = opacity
            if filter:
                bg_image.filter = filter

    # list-style only:

    def get_level_style(self, level):
        if self.family != "list":
            return None
        level_styles = (
            "(text:list-level-style-number"
            "|text:list-level-style-bullet"
            "|text:list-level-style-image)"
        )
        return _get_element(self, level_styles, 0, level=level)

    def set_level_style(
        self,
        level,
        num_format=None,
        bullet_char=None,
        url=None,
        display_levels=None,
        prefix=None,
        suffix=None,
        start_value=None,
        style=None,
        clone=None,
    ):
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
        if clone is not None:
            level_style = clone.clone
            was_created = True
        else:
            level_style = self.get_level_style(level)
            if level_style is None:
                level_style = Element.from_tag(level_style_name)
                was_created = True
        # Transmute if the type changed
        if level_style.tag != level_style_name:
            print("warn: different style", level_style_name, level_style.tag)
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
            level_style.text_style = style
        # Commit the creation
        if was_created:
            self.append(level_style)
        return level_style

    # page-layout only:

    def get_header_style(self):
        if self.family != "page-layout":
            return None
        return self.get_element("style:header-style")

    def set_header_style(self, new_style):
        if self.family != "page-layout":
            return
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)

    def get_footer_style(self):
        if self.family != "page-layout":
            return None
        return self.get_element("style:footer-style")

    def set_footer_style(self, new_style):
        if self.family != "page-layout":
            return
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)

    # master-page only:

    def __set_header_or_footer(self, text_or_element, name="header", style="Header"):
        if name == "header":
            header_or_footer = self.get_page_header()
        else:
            header_or_footer = self.get_page_footer()
        if header_or_footer is None:
            header_or_footer = Element.from_tag("style:" + name)
            self.append(header_or_footer)
        else:
            header_or_footer.clear()
        if not isiterable(text_or_element):
            # Already a header or footer?
            if isinstance(
                text_or_element, Element
            ) and text_or_element.tag == "style:%s" % to_str(name):
                self.delete(header_or_footer)
                self.append(text_or_element)
                return
            text_or_element = [text_or_element]
        # FIXME cyclic import
        for item in text_or_element:
            if isinstance(item, str):
                paragraph = Paragraph(item, style=style)
                header_or_footer.append(paragraph)
            elif isinstance(item, Element):
                header_or_footer.append(item)

    def get_page_header(self):
        """Get the element that contains the header contents.

        If None, no header was set.
        """
        if self.family != "master-page":
            return None
        return self.get_element("style:header")

    def set_page_header(self, text_or_element):
        """Create or replace the header by the given content. It can already
        be a complete header.

        If you only want to update the existing header, get it and use the
        API.

        Arguments:

            text_or_element -- str or Element or a list of them
        """
        if self.family != "master-page":
            return None
        return self.__set_header_or_footer(text_or_element)

    def get_page_footer(self):
        """Get the element that contains the footer contents.

        If None, no footer was set.
        """
        if self.family != "master-page":
            return None
        return self.get_element("style:footer")

    def set_page_footer(self, text_or_element):
        """Create or replace the footer by the given content. It can already
        be a complete footer.

        If you only want to update the existing footer, get it and use the
        API.

        Arguments:

            text_or_element -- str or Element or a list of them
        """
        if self.family != "master-page":
            return None
        return self.__set_header_or_footer(
            text_or_element, name="footer", style="Footer"
        )

    # font-face only:

    def set_font(self, name, family=None, family_generic=None, pitch="variable"):
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
    _properties = (
        ("name", "style:name", None),
        ("display_name", "style:display-name", None),
        ("svg_font_family", "svg:font-family", None),
        ("font_family_generic", "style:font-family-generic", None),
        ("font_pitch", "style:font-pitch", None),
        ("position", "style:position", "background-image"),
        ("repeat", "style:repeat", "background-image"),
        ("opacity", "draw:opacity", "background-image"),
        ("filter", "style:filter-name", "background-image"),
        ("text_style", "text:style-name", None),
    )

    def __init__(
        self,
        name=None,
        display_name=None,
        position=None,
        repeat=None,
        opacity=None,
        filter=None,
        # Every other property
        **kw,
    ):
        kw["family"] = "background-image"
        super().__init__(**kw)
        if self._do_init:
            kw.pop("tag", None)
            kw.pop("tag_or_elem", None)
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
            for p in BackgroundImage._properties:
                k = p[0]
                attr = p[1]
                if k in kw:
                    self.set_style_attribute(attr, kw[k])


BackgroundImage._define_attribut_property()


# Some predefined styles
def default_number_style():
    return Element.from_tag(
        """<number:number-style style:name="lpod-default-number-style">
           <number:number number:decimal-places="2"
            number:min-integer-digits="1"/>
           </number:number-style>"""
    )


def default_percentage_style():
    return Element.from_tag(
        """<number:percentage-style
                  style:name="lpod-default-percentage-style">
                  <number:number number:decimal-places="2"
                   number:min-integer-digits="1"/>
                  <number:text>%</number:text>
                  </number:percentage-style>"""
    )


def default_time_style():
    return Element.from_tag(
        """<number:time-style style:name="lpod-default-time-style">
             <number:hours number:style="long"/>
             <number:text>:</number:text>
             <number:minutes number:style="long"/>
             <number:text>:</number:text>
             <number:seconds number:style="long"/>
           </number:time-style>"""
    )


def default_date_style():
    return Element.from_tag(
        """<number:date-style style:name="lpod-default-date-style">
             <number:year number:style="long"/>
             <number:text>-</number:text>
             <number:month number:style="long"/>
             <number:text>-</number:text>
             <number:day number:style="long"/>
           </number:date-style>"""
    )


def default_boolean_style():
    return Element.from_tag(
        """<number:boolean-style style:name="lpod-default-boolean-style">
             <number:boolean/>
           </number:boolean-style>"""
    )


def default_currency_style():
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
register_element_class(Style, STYLES_TO_REGISTER)
