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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""get_value() and other utilities
"""
from datetime import date, datetime, timedelta
from decimal import Decimal as dec
from os import getcwd
from os.path import splitdrive, join, sep
from re import search
from sys import _getframe, modules
from .const import ODF_PROPERTIES

from .datatype import Boolean, Date, DateTime, Duration

# CELL_TYPES = 'boolean currency date float percentage string time'.split()

# STYLE_FAMILIES = ('paragraph', 'text', 'section', 'table', 'table-column',
#                   'table-row', 'table-cell', 'table-page', 'chart',
#                   'default', 'drawing-page', 'graphic', 'presentation',
#                   'control', 'ruby', 'list', 'number', 'page-layout',
#                   'presentation-page-layout', 'font-face', 'master-page')

# NOTE_CLASSES = ('footnote', 'endnote')

# This DPI is computed to have:
# 640 px (width of your wiki) <==> 17 cm (width of a normal ODT page)
DPI = 640 * dec("2.54") / 17

######################################################################
# Private API
######################################################################


def to_bytes(value):
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def to_str(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _make_xpath_query(
    element_name,
    family=None,
    text_style=None,
    draw_id=None,
    draw_name=None,
    draw_style=None,
    draw_text_style=None,
    table_name=None,
    table_style=None,
    style_name=None,
    display_name=None,
    note_class=None,
    text_id=None,
    text_name=None,
    change_id=None,
    office_name=None,
    office_title=None,
    outline_level=None,
    level=None,
    page_layout=None,
    master_page=None,
    parent_style=None,
    presentation_class=None,
    position=None,
    **kw
):
    query = [to_str(element_name)]
    attributes = kw
    if text_style:
        attributes["text:style-name"] = text_style
    if family and family in FAMILY_ODF_STD:
        attributes["style:family"] = family
    if draw_id:
        attributes["draw:id"] = draw_id
    if draw_name:
        attributes["draw:name"] = draw_name
    if draw_style:
        attributes["draw:style-name"] = draw_style
    if draw_text_style:
        attributes["draw:text-style-name"] = draw_text_style
    if table_name:
        attributes["table:name"] = table_name
    if table_style:
        attributes["table:style-name"] = table_style
    if style_name:
        attributes["style:name"] = style_name
    if display_name:
        attributes["style:display-name"] = display_name
    if note_class:
        attributes["text:note-class"] = note_class
    if text_id:
        attributes["text:id"] = text_id
    if text_name:
        attributes["text:name"] = text_name
    if change_id:
        attributes["text:change-id"] = change_id
    if office_name:
        attributes["office:name"] = office_name
    if office_title:
        attributes["office:title"] = office_title
    if outline_level:
        attributes["text:outline-level"] = outline_level
    if level:
        attributes["text:level"] = level
    if page_layout:
        attributes["style:page-layout-name"] = page_layout
    if master_page:
        attributes["draw:master-page-name"] = master_page
    if parent_style:
        attributes["style:parent-style-name"] = parent_style
    if presentation_class:
        attributes["presentation:class"] = presentation_class
    # Sort attributes for reproducible test cases
    for qname in sorted(attributes):
        value = attributes[qname]
        if value is True:
            query.append("[@%s]" % to_str(qname))
        else:
            query.append('[@%s="%s"]' % (to_str(qname), value))
    query = "".join(query)
    if position is not None:
        # A position argument that mimics the behaviour of a python's list
        if position >= 0:
            position = "%s" % (position + 1)
        elif position == -1:
            position = "last()"
        else:
            position = "last()-%s" % (abs(position) - 1)
        query = "(%s)[%s]" % (query, position)
    # print(query)
    return query


# style:family as defined by ODF 1.2, e.g. xxx possibily for:
# 'style:style style:family="xxx"'
FAMILY_ODF_STD = set(
    (
        "chart drawing-page graphic paragraph"
        " presentation ruby section table table-cell"
        " table-column table-row text"
    ).split()
)

_BASE_FAMILY_MAP = {k: "style:style" for k in FAMILY_ODF_STD}

_FALSE_FAMILY_MAP = {
    "background-image": "style:background-image",
    "date": "number:date-style",
    "font-face": "style:font-face",
    "list": "text:list-style",
    "master-page": "style:master-page",
    "marker": "draw:marker",
    "number": "number:number-style",
    "outline": "text:outline-style",
    "page-layout": "style:page-layout",
    "percentage": "number:percentage-style",
    "presentation-page-layout": "style:presentation-page-layout",
    "time": "number:time-style",
    "boolean": "number:boolean-style",
    "currency": "number:currency-style",
    "tab-stop": "style:tab-stop",
}

OTHER_STYLES = set(
    (
        "style:default-style style:header-style"
        " style:footer-style text:list-level-style-bullet"
        " text:list-level-style-image"
        " text:list-level-style-number"
    ).split()
)
SUBCLASS_STYLES = {"background-image"}

FAMILY_MAPPING = {**_BASE_FAMILY_MAP, **_FALSE_FAMILY_MAP}

FALSE_FAMILY_MAP_REVERSE = {v: k for k, v in _FALSE_FAMILY_MAP.items()}
SUBCLASSED_STYLES = {"style:background-image"}
STYLES_TO_REGISTER = (set(FAMILY_MAPPING.values()) | OTHER_STYLES) - SUBCLASSED_STYLES


def _family_style_tagname(family):
    if family not in FAMILY_MAPPING:
        raise ValueError("unknown family: %s" % family)
    return FAMILY_MAPPING[family]


def _get_style_family(name):
    for family, (tagname, _famattr) in FAMILY_MAPPING.items():
        if tagname == name:
            return family
    return None


def _expand_properties(properties):
    # This mapping is not exhaustive, it only contains cases where replacing
    # '_' with '-' and adding the "fo:" prefix is not enough
    mapping = {  # text
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

    def map_key(key):
        if key in ODF_PROPERTIES:
            return key
        key = mapping.get(key, key).replace("_", "-")
        if ":" not in key:
            key = "fo:" + key
        if key in ODF_PROPERTIES:
            return key
        return None

    if isinstance(properties, dict):
        expanded = {}
        for key in sorted(properties.keys()):
            prop_key = map_key(key)
            if not prop_key:
                continue
            expanded[prop_key] = to_str(properties[key])

    elif isinstance(properties, list):
        expanded = list(filter(None, (map_key(key) for key in properties)))
    return expanded


def _merge_dicts(d, *args, **kw):
    """Merge two or more dictionaries into a new dictionary object."""
    new_d = d.copy()
    for dic in args:
        new_d.update(dic)
    new_d.update(kw)
    return new_d


# Non-public yet useful helpers


def _get_elements(
    context,
    element_name,
    content=None,
    url=None,
    svg_title=None,
    svg_desc=None,
    dc_creator=None,
    dc_date=None,
    **kw
):
    query = _make_xpath_query(element_name, **kw)
    elements = context.get_elements(query)
    # Filter the elements with the regex (TODO use XPath)
    if content is not None:
        elements = [element for element in elements if element.match(content)]
    if url is not None:
        filtered = []
        for element in elements:
            url_attr = element.get_attribute("xlink:href")
            if search(url, url_attr) is not None:
                filtered.append(element)
        elements = filtered
    if dc_date is not None:
        # XXX Date or DateTime?
        dc_date = DateTime.encode(dc_date)
    for variable, childname in [
        (svg_title, "svg:title"),
        (svg_desc, "svg:desc"),
        (dc_creator, "descendant::dc:creator"),
        (dc_date, "descendant::dc:date"),
    ]:
        if not variable:
            continue
        filtered = []
        for element in elements:
            child = element.get_element(childname)
            if child and child.match(variable):
                filtered.append(element)
        elements = filtered
    return elements


def _get_element(context, element_name, position, **kw):
    # TODO Transmit position not to load the whole list
    result = _get_elements(context, element_name, **kw)
    try:
        return result[position]
    except IndexError:
        return None


def _set_value_and_type(element, value=None, value_type=None, text=None, currency=None):
    # Remove possible previous value and type
    for name in (
        "office:value-type",
        "office:boolean-value",
        "office:value",
        "office:date-value",
        "office:string-value",
        "office:time-value",
        "table:formula",
        "office:currency",
        "calcext:value-type",
        "loext:value-type",
    ):
        try:
            element.del_attribute(name)
        except KeyError:
            pass
    value = to_str(value)
    value_type = to_str(value_type)
    text = to_str(text)
    currency = to_str(currency)
    if value is None:
        try:
            element.del_attribute(name)
        except KeyError:
            pass
        element._erase_text_content()
        return text
    if isinstance(value, bool):
        if value_type is None:
            value_type = "boolean"
        if text is None:
            text = "true" if value else "false"
        value = Boolean.encode(value)
    elif isinstance(value, (int, float, dec)):
        if value_type == "percentage":
            text = "%d %%" % int(value * 100)
        if value_type is None:
            value_type = "float"
        if text is None:
            text = str(value)
        value = str(value)
    elif isinstance(value, datetime):
        if value_type is None:
            value_type = "date"
        if text is None:
            text = str(DateTime.encode(value))
        value = DateTime.encode(value)
    elif isinstance(value, date):
        if value_type is None:
            value_type = "date"
        if text is None:
            text = str(Date.encode(value))
        value = Date.encode(value)
    elif isinstance(value, str):
        if value_type is None:
            value_type = "string"
        if text is None:
            text = str(value)
    elif isinstance(value, timedelta):
        if value_type is None:
            value_type = "time"
        if text is None:
            text = str(Duration.encode(value))
        value = Duration.encode(value)
    elif value is not None:
        raise TypeError('type "%s" is unknown' % type(value))

    if value_type is not None:
        element.set_attribute("office:value-type", value_type)
        element.set_attribute("calcext:value-type", value_type)
    if value_type == "boolean":
        element.set_attribute("office:boolean-value", value)
    elif value_type == "currency":
        element.set_attribute("office:value", value)
        element.set_attribute("office:currency", currency)
    elif value_type == "date":
        element.set_attribute("office:date-value", value)
    elif value_type in ("float", "percentage"):
        element.set_attribute("office:value", value)
        element.set_attribute("calcext:value", value)
    elif value_type == "string":
        element.set_attribute("office:string-value", value)
    elif value_type == "time":
        element.set_attribute("office:time-value", value)

    return text


######################################################################
# Public API
######################################################################
def get_value(element, value_type=None, try_get_text=True, get_type=False):
    """Only for "with office:value-type" elements, not for meta fields"""
    if value_type is None:
        value_type = element.get_attribute("office:value-type")
    # value_type = to_str(value_type)
    if value_type == "boolean":
        value = element.get_attribute("office:boolean-value")
        if get_type:
            return (value, value_type)
        return value  # value is already decoded by get_attribute for booleans
    if value_type in {"float", "percentage", "currency"}:
        value = dec(element.get_attribute("office:value"))
        # Return 3 instead of 3.0 if possible
        if int(value) == value:
            if get_type:
                return (int(value), value_type)
            return int(value)
        if get_type:
            return (value, value_type)
        return value
    if value_type == "date":
        value = element.get_attribute("office:date-value")
        if "T" in value:
            if get_type:
                return (DateTime.decode(value), value_type)
            return DateTime.decode(value)
        if get_type:
            return (Date.decode(value), value_type)
        return Date.decode(value)
    if value_type == "string":
        value = element.get_attribute("office:string-value")
        if value is not None:
            if get_type:
                return (str(value), value_type)
            return str(value)
        if try_get_text:
            value = []
            for para in element.get_elements("text:p"):
                value.append(para.text_recursive)
            if value:
                if get_type:
                    return ("\n".join(value), value_type)
                return "\n".join(value)
        if get_type:
            return (None, value_type)
        return None
    if value_type == "time":
        value = Duration.decode(element.get_attribute("office:time-value"))
        if get_type:
            return (value, value_type)
        return value
    if value_type is None:
        if get_type:
            return (None, None)
        return None

    raise ValueError('unexpected value type "%s"' % value_type)


def set_value(element, value):
    """Only for "with office:value-type" elements"""
    tag = element.tag
    # A table:cell ?
    if tag == "table:table-cell":
        element.clear()
        text = _set_value_and_type(element, value=value)
        element.text_content = text
        return
    # A text:variable-set ?
    if tag == "text:variable-set":
        name = element.get_attribute("text:name")
        display = element.get_attribute("text:display")
        element.clear()
        text = _set_value_and_type(element, value=value)
        element.set_attribute("text:name", name)
        if display is not None:
            element.set_attribute("text:display", display)
        element.text = text
        return
    # A text:user-field-decl ?
    if tag == "text:user-field-decl":
        name = element.get_attribute("text:name")
        element.clear()
        _set_value_and_type(element, value=value)
        element.set_attribute("text:name", name)
        return
    # Else => error
    raise ValueError('set_value: unexpected element "%s"' % tag)


def oooc_to_ooow(formula):
    """Convert (proprietary) formula from calc format to writer format.

    Arguments:

        formula -- str

    Return: str
    """
    prefix, formula = formula.split(":=", 1)
    assert "oooc" in prefix
    # Convert cell addresses
    formula = formula.replace("[.", "<").replace(":.", ":").replace("]", ">")
    # Convert functions
    formula = formula.replace("SUM(", "sum ").replace(")", "")
    return "ooow:" + formula


# def obsolete(old_name, new_func, *args, **kw):
#     def decorate(*dec_args, **dec_kw):
#         new_name = new_func.__name__
#         if args:
#             new_name += '(' + ', '.join(repr(x) for x in args) + ')'
#         message = '"%s" is obsolete, call "%s" instead' % (old_name, new_name)
#         warn(message, category=DeprecationWarning)
#         return new_func(*(dec_args + args), **dec_kw)
#
#     return decorate


def isiterable(obj):
    if isinstance(obj, (str, bytes)):
        return False
    try:
        iter(obj)
    except TypeError:
        return False
    return True
