# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Classes related to "style:master-page"."""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class
from .mixin_toc import TocMixin
from .office_forms import OfficeFormsMixin
from .section import SectionMixin
from .style_base import StyleBase
from .tracked_changes import TrackedChangesMixin
from .user_field_declaration import UserFieldDeclContMixin
from .variable_declaration import VarDeclMixin


class StyleMasterPage(OfficeFormsMixin, StyleBase):
    """Container of headers and footers, "style:master-page".

    In text and spreadsheet documents, the "style:master-page" element contains
    the content of headers and footers. For these types of documents, consumers
    may generate a sequence of pages by making use of a single master page or a
    set of master pages.

    In drawing and presentation documents, the "style:master-page" element is
    used to define master pages as common backgrounds for drawing pages. Each
    drawing page is directly linked to one master page, which is specified by
    the draw:master-page-name attribute of the drawing pages style.

    Master pages are contained in the "office:master-styles" element.

    All documents shall contain at least one master page element.

    If a text or spreadsheet document is displayed in a paged layout, master
    pages are used to generate a sequence of pages containing the document
    content. When a page is created, an empty page is generated with the
    properties of the master page and the static content of the master page.
    The body of the page is then filled with content. A single master pages can
    be used to created multiple pages within a document.

    In text and spreadsheet documents, a master page can be assigned to
    paragraph and table styles using a style:master-page-name attribute. Each
    time the paragraph or table style is applied to text, a page break is
    inserted before the paragraph or table. A page that starts at the page
    break position uses the specified master page.

    In drawings and presentations, master pages can be assigned to drawing
    pages using a style:parent-style-name attribute.

    The "style:master-page" element is usable within the following element:
    "office:master-styles".
    """

    # The <style:master-page> element has the following attributes:
    # draw:style-name
    # style:display-name
    # style:name
    # style:next-style-name
    # style:page-layout-name

    _tag: str = "style:master-page"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "style:name"),
        PropDef("display_name", "style:display-name"),
        PropDef("page_layout", "style:page-layout-name", "master-page"),
        PropDef(
            "next_style",
            "style:next-style-name",
            "master-page",
        ),
        PropDef("draw_style_name", "draw:style-name"),
    )

    def __init__(
        self,
        name: str | None = None,
        display_name: str | None = None,
        page_layout: str | None = None,
        next_style: str | None = None,
        draw_style_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a StyleMasterPage.

        The master page's `name` is not mandatory at creation but becomes
        required when inserted into a document as a common style.
        The `display_name` is the name visible to the user in office applications.

        Args:
            name: The internal name of the master page style.
            display_name: The user-facing display name of the style.
            page_layout: The name of the page layout style to use.
            next_style: The name of the next master page style to apply.
            draw_style_name: The name of the drawing style to apply.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        self._family = "master-page"
        tag_or_elem = kwargs.get("tag_or_elem")
        if tag_or_elem is None:
            kwargs["tag"] = "style:master-page"
        Element.__init__(self, **kwargs)
        if self._do_init:
            # print("_do_init")
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            if name:
                self.name = name
            if display_name:
                self.display_name = display_name
            if page_layout:
                self.page_layout = page_layout
            if next_style:
                self.next_style = next_style
            if draw_style_name:
                self.draw_style_name = draw_style_name

    @property
    def family(self) -> str | None:
        """Get the family of the style.

        For `StyleMasterPage`, this is always "master-page".
        """
        return self._family

    @family.setter
    def family(self, family: str | None) -> None:
        """Setter for the family property (no-op as family is fixed)."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} family={self.family} name={self.name}>"

    def _set_header_or_footer(
        self,
        text_or_element: str | Element | list[Element | str],
        name: str = "header",
        style: str = "Header",
    ) -> None:
        """Internal helper to set the content of a page header or footer.

        This method replaces existing content or creates a new header/footer
        element if one doesn't exist. It can accept raw text, an `Element`,
        or a list of `Element`s or strings.

        Args:
            text_or_element: The content to set. Can be a string, an `Element`,
                or an iterable of strings and/or `Element`s.
            name: The name of the part to set ("header" or "footer").
            style: The default style name to apply to new paragraphs
                created from string content.
        """
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
                paragraph.append_plain_text(item)  # type: ignore
                paragraph.style = style  # type: ignore
                header_or_footer.append(paragraph)
            elif isinstance(item, Element):
                header_or_footer.append(item)

    def get_page_header(self) -> Element | None:
        """Get the `style:header` element containing the header contents.

        Returns:
            Element | None: The `style:header` element, or `None` if no header
                content is defined for this master page.
        """
        return self.get_element("style:header")

    def set_page_header(
        self,
        text_or_element: str | Element | list[Element | str],
    ) -> None:
        """Set or replace the content of the page header.

        This method uses `_set_header_or_footer` to update the header's content.
        You can provide raw text, an `Element`, or a list of content to replace
        the existing header. To modify the existing header without replacing it
        entirely, retrieve it first using `get_page_header` and use its API.

        Args:
            text_or_element: The new content for the header.
        """
        self._set_header_or_footer(text_or_element)

    def get_page_footer(self) -> Element | None:
        """Get the `style:footer` element containing the footer contents.

        Returns:
            Element | None: The `style:footer` element, or `None` if no footer
                content is defined for this master page.
        """
        return self.get_element("style:footer")

    def set_page_footer(
        self,
        text_or_element: str | Element | list[Element | str],
    ) -> None:
        """Set or replace the content of the page footer.

        This method uses `_set_header_or_footer` to update the footer's content.
        You can provide raw text, an `Element`, or a list of content to replace
        the existing footer. To modify the existing footer without replacing it
        entirely, retrieve it first using `get_page_footer` and use its API.

        Args:
            text_or_element: The new content for the footer.
        """
        self._set_header_or_footer(text_or_element, name="footer", style="Footer")

    def set_font(
        self,
        name: str,
        family: str | None = None,
        family_generic: str | None = None,
        pitch: str = "variable",
    ) -> None:
        """This method is not applicable to `StyleMasterPage` and does nothing."""


StyleMasterPage._define_attribut_property()


class StyleHeader(
    TocMixin,
    UserFieldDeclContMixin,
    VarDeclMixin,
    TrackedChangesMixin,
    SectionMixin,
    StyleBase,
):
    """Content of a header in a StyleMasterPage, tag "style:header".

    The "style:display" attribute specifies whether the header is displayed or
    not ("true" or "false"). The default value is "true".
    """

    _tag: str = "style:header"

    def __init__(
        self,
        display: str | bool | None = True,
        # Every other property
        **kwargs: Any,
    ) -> None:
        """Initialize a StyleHeader element.

        Args:
            display: Specifies whether the header is displayed.
                Can be "true", "false", or a boolean. Defaults to True.
            **kwargs: Additional keyword arguments for the parent `Element` class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            kwargs.pop("tag", None)
            kwargs.pop("tag_or_elem", None)
            self.display = display

    @property
    def display(self) -> bool:
        """Get the display status of the header.

        Returns:
            bool: True if the header is displayed, False otherwise.
        """
        return self._get_attribute_bool_default("style:display", True)

    @display.setter
    def display(self, display: bool | str | None) -> None:
        """Set the display status of the header.

        Args:
            display: The display status. Can be a boolean,
                or "true"/"false" string.
        """
        self._set_attribute_bool_default("style:display", display, True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class StyleFooter(StyleHeader):
    """Content of a footer in a StyleMasterPage, tag "style:footer".

    The "style:display" attribute specifies whether the footer is displayed or
    not ("true" or "false"). The default value is "true".
    """

    _tag: str = "style:footer"


class StyleHeaderLeft(StyleHeader):
    """Content of a left page header in a StyleMasterPage, tag "style:header-
    left".

    If left page different from the right page in a "style:master-page".

    The "style:display" attribute specifies whether the header is displayed or
    not ("true" or "false"). The default value is "true".
    """

    _tag: str = "style:header-left"


class StyleHeaderFirst(StyleHeader):
    """Content of a header for a first page, if different from the left/right
    page in a "style:master-page" element, tag "style:header-first"

    The term "first page" means the first page to which the page style is
    applied, regardless of any numbering. If a different page style is
    applied in between two applications of a page style that has the
    "style:header-first" element, each of the applications of the page
    style has its own first page.

    The "style:display" attribute specifies whether the header is displayed or
    not ("true" or "false"). The default value is "true".

    New in ODFv1.3.
    """

    _tag: str = "style:header-first"


class StyleFooterLeft(StyleHeader):
    """Content of a left page footer in a StyleMasterPage, tag "style:footer-
    left".

    If left page different from the right page in a "style:master-page".

    The "style:display" attribute specifies whether the footer is displayed or
    not ("true" or "false"). The default value is "true".
    """

    _tag: str = "style:footer-left"


class StyleFooterFirst(StyleHeader):
    """Content of a footer for a first page, if different from the left/right
    page in a "style:master-page" element, tag "style:footer-first".

    The term "first page" means the first page to which the page style is
    applied, regardless of any numbering. If a different page style is
    applied in between two applications of the page style, that has the
    "style:footer-first" element, each of the applications of the page style
    has its own first page.

    New in ODFv1.3.
    """

    _tag: str = "style:footer-first"


StyleFooterLeft._define_attribut_property()

register_element_class(StyleFooter)
register_element_class(StyleFooterFirst)
register_element_class(StyleFooterLeft)
register_element_class(StyleHeader)
register_element_class(StyleHeaderFirst)
register_element_class(StyleHeaderLeft)
register_element_class(StyleMasterPage)
