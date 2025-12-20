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
"""TOC class for "text:table-of-content" tag and TabStopStyle,
TocEntryTemplate, IndexBody, IndexTitle, IndexTitleTemplate related
classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, cast

from .element import FIRST_CHILD, Element, PropDef, PropDefBool, register_element_class
from .mixin_md import MDToc
from .mixin_toc import TocMixin
from .section import SectionMixin
from .style import Style

if TYPE_CHECKING:
    from .document import Document


def _toc_entry_style_name(level: int) -> str:
    """Return the style name of an entry of the TOC.

    Args:
        level: The outline level of the TOC entry.

    Returns:
        str: The generated style name.
    """
    return f"odfto_toc_level_{level}"


class TabStopStyle(Element):
    """Style for a tab-stop in a TOC entry, represented by "style:tab-stop".

    This class defines the visual properties of tab stops, such as their
    position, alignment, and leader style.

    Attributes:
        style_char (str, optional): The character used for the tab stop.
        leader_color (str, optional): The color of the leader line.
        leader_style (str, optional): The style of the leader line (e.g.,
            'dotted', 'solid').
        leader_text (str, optional): The text to use as a leader.
        leader_text_style (str, optional): The style of the leader text.
        leader_type (str, optional): The type of leader (e.g., 'none',
            'solid').
        leader_width (str, optional): The width of the leader line.
        style_position (str, optional): The position of the tab stop (e.g.,
            '1.25cm').
        style_type (str, optional): The alignment type of the tab stop
            (e.g., 'left', 'right').
    """

    _tag = "style:tab-stop"
    _properties = (
        PropDef("style_char", "style:char"),
        PropDef("leader_color", "style:leader-color"),
        PropDef("leader_style", "style:leader-style"),
        PropDef("leader_text", "style:leader-text"),
        PropDef("leader_text_style", "style:leader-text-style"),
        PropDef("leader_type", "style:leader-type"),
        PropDef("leader_width", "style:leader-width"),
        PropDef("style_position", "style:position"),
        PropDef("style_type", "style:type"),
    )

    def __init__(
        self,
        style_char: str | None = None,
        leader_color: str | None = None,
        leader_style: str | None = None,
        leader_text: str | None = None,
        leader_text_style: str | None = None,
        leader_type: str | None = None,
        leader_width: str | None = None,
        style_position: str | None = None,
        style_type: str | None = None,
        **kwargs: Any,
    ):
        """Initializes a TabStopStyle element.

        Args:
            style_char: The character for the tab stop.
            leader_color: Color of the leader line.
            leader_style: Style of the leader line.
            leader_text: Text to use as a leader.
            leader_text_style: Style of the leader text.
            leader_type: Type of leader.
            leader_width: Width of the leader line.
            style_position: Position of the tab stop.
            style_type: Alignment type of the tab stop.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if style_char:
                self.style_char = style_char
            if leader_color:
                self.leader_color = leader_color
            if leader_style:
                self.leader_style = leader_style
            if leader_text:
                self.leader_text = leader_text
            if leader_text_style:
                self.leader_text_style = leader_text_style
            if leader_type:
                self.leader_type = leader_type
            if leader_width:
                self.leader_width = leader_width
            if style_position:
                self.style_position = style_position
            if style_type:
                self.style_type = style_type
        else:
            pass  # pragma: nocover


TabStopStyle._define_attribut_property()


def default_toc_level_style(level: int) -> Style:
    """Generate an automatic default style for the given TOC level.

    Args:
        level: The outline level for which to create the style.

    Returns:
        Style: The generated style for the TOC level.
    """
    tab_stop = TabStopStyle(style_type="right", leader_style="dotted", leader_text=".")
    position = 17.5 - (0.5 * level)
    tab_stop.style_position = f"{position}cm"
    tab_stops = Element.from_tag("style:tab-stops")
    tab_stops.append(tab_stop)
    properties = Element.from_tag("style:paragraph-properties")
    properties.append(tab_stops)
    toc_style_level = Style(
        family="paragraph",
        name=_toc_entry_style_name(level),
        parent=f"Contents_20_{level}",
    )
    toc_style_level.append(properties)
    return toc_style_level


class TOC(MDToc, Element):
    """A table of content, "text:table-of-content".

    The "text:table-of-content" element represents a table of contents for a
    document. The items that can be listed in a table of contents are:

      - Headings (as defined by the outline structure of the document), up to
        a selected level.

      - Table of contents index marks.

      - Paragraphs formatted with specified paragraph styles.

    Attributes:
        name (str): The name of the table of contents.
        style (str, optional): The style name for the TOC.
        xml_id (str, optional): The XML ID of the TOC.
        protected (bool): Whether the TOC is protected from manual changes.
        protection_key (str, optional): The key for protection.
        protection_key_digest_algorithm (str, optional): The algorithm for
            the protection key digest.
    """

    _tag = "text:table-of-content"
    _properties = (
        PropDef("name", "text:name"),
        PropDef("style", "text:style-name"),
        PropDef("xml_id", "xml:id"),
        PropDef("protected", "text:protected"),
        PropDef("protection_key", "text:protection-key"),
        PropDef(
            "protection_key_digest_algorithm", "text:protection-key-digest-algorithm"
        ),
    )

    def __init__(
        self,
        title: str = "Table of Contents",
        name: str | None = None,
        protected: bool = True,
        outline_level: int = 0,
        style: str | None = None,
        title_style: str = "Contents_20_Heading",
        entry_style: str = "Contents_20_%d",
        **kwargs: Any,
    ) -> None:
        """Initializes a TOC (Table of Contents) element.

        Default parameters are what most people use: protected from manual
        modifications and not limited in title levels.

        The name is mandatory and derived automatically from the title if not
        given. Provide one in case of a conflict with other TOCs in the same
        document.

        Args:
            title: The title of the TOC (e.g., "Table of Contents").
            name: The name of the TOC element. If not
                provided, it's generated from the title.
            protected: If True, the TOC is protected from manual
                modifications.
            outline_level: The maximum outline level to include in the
                TOC. 0 means all levels.
            style: The style name for the TOC container.
            title_style: The style for the TOC's main title.
            entry_style: A format string for the style of each TOC
                entry (e.g., "Contents_20_%d").
        """
        super().__init__(**kwargs)
        if self._do_init:
            if style:
                self.style = style
            if protected:
                self.protected = protected
            if name is None:
                self.name = f"{title}1"
            # Create the source template
            toc_source = self.create_toc_source(
                title, outline_level, title_style, entry_style
            )
            self.append(toc_source)
            # Create the index body automatically with the index title
            if title:
                # This style is in the template document
                self.set_toc_title(title, text_style=title_style)

    @staticmethod
    def create_toc_source(
        title: str,
        outline_level: int,
        title_style: str,
        entry_style: str,
    ) -> Element:
        """Create the 'text:table-of-content-source' element for a TOC.

        This element defines the structure and appearance of the TOC.

        Args:
            title: The title of the TOC.
            outline_level: The maximum outline level to include.
            title_style: The style for the TOC's title.
            entry_style: The format string for entry styles.

        Returns:
            Element: The newly created 'text:table-of-content-source'
                element.
        """
        toc_source = Element.from_tag("text:table-of-content-source")
        toc_source.set_attribute("text:outline-level", str(outline_level))
        if title:
            title_template = IndexTitleTemplate()
            if title_style:
                # This style is in the template document
                title_template.style = title_style
            title_template.text = title
            toc_source.append(title_template)
        for level in range(1, 11):
            template = TocEntryTemplate(outline_level=level)
            if entry_style:
                template.style = entry_style % level
            toc_source.append(template)
        return toc_source

    def __str__(self) -> str:
        return self.get_formatted_text()

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Returns the formatted text content of the TOC.

        Args:
            context: A context dictionary for formatting.
                If 'rst_mode' is True, it returns a reStructuredText
                'contents' directive.

        Returns:
            str: The formatted text of the TOC.
        """
        index_body = cast(Union[None, IndexBody], self.get_element(IndexBody._tag))

        if index_body is None:
            return ""
        if context is None:
            context = {}
        if context.get("rst_mode"):
            return "\n.. contents::\n\n"

        result = []
        for element in index_body.children:
            if element.tag == "text:index-title":
                for child_element in element.children:
                    result.append(child_element.get_formatted_text(context).strip())
            else:
                result.append(element.get_formatted_text(context).strip())
        return "\n".join(x for x in result if x)

    @property
    def outline_level(self) -> int | None:
        """The outline level of the TOC.

        This property controls the maximum heading level that will be included
        in the table of contents. A value of 0 means all levels are included.
        """
        source = self.get_element("text:table-of-content-source")
        if source is None:
            return None
        return source.get_attribute_integer("text:outline-level")

    @outline_level.setter
    def outline_level(self, level: int) -> None:
        source = self.get_element("text:table-of-content-source")
        if source is None:
            source = Element.from_tag("text:table-of-content-source")
            self.insert(source, FIRST_CHILD)
        source.set_attribute("text:outline-level", str(level))

    @property
    def body(self) -> IndexBody | None:
        """The body of the TOC ('text:index-body').

        This property provides access to the 'text:index-body' element, which
        contains the actual entries of the table of contents.
        """
        return cast(Union[None, IndexBody], self.get_element(IndexBody._tag))

    @body.setter
    def body(self, body: Element | None = None) -> Element | None:
        old_body = self.body
        if old_body is not None:
            self.delete(old_body)
        if body is None:
            body = Element.from_tag("text:index-body")
        self.append(body)
        return body

    def get_title(self) -> str:
        """Returns the title of the TOC.

        Returns:
            str: The title of the TOC.
        """
        index_body = self.body
        if index_body is None:
            return ""
        index_title = cast(
            Union[None, IndexTitle], index_body.get_element(IndexTitle._tag)
        )
        if index_title is None:
            return ""
        return index_title.text_content

    def set_toc_title(
        self,
        title: str,
        style: str | None = None,
        text_style: str | None = None,
    ) -> None:
        """Sets the title of the TOC.

        Args:
            title: The new title for the TOC.
            style: The style for the index title element.
            text_style: The style for the title's paragraph.
        """
        index_body = self.body
        if index_body is None:
            self.body = None  # this ceates a new index_body
            index_body = cast(IndexBody, self.body)
        index_title = cast(
            Union[None, IndexTitle], index_body.get_element(IndexTitle._tag)
        )
        if index_title:
            style = style or index_title.style
            if not text_style:
                index_title_paragraph = index_title.get_element("text:p")
                if index_title_paragraph:
                    text_style = index_title_paragraph.style  # type: ignore[attr-defined]
            name = index_title.name
            index_title.delete()
        else:
            name = f"{self.name}_Head"
        index_title = IndexTitle(
            name=name, style=style, title_text=title, text_style=text_style
        )
        index_body.append(index_title)

    @staticmethod
    def _header_numbering(level_indexes: dict[int, int], level: int) -> str:
        """Return the header hierarchical number (like "1.2.3.").

        Args:
            level_indexes: A dictionary to track numbering
                at each level.
            level: The current header level.

        Returns:
            str: The hierarchical number string.
        """
        numbers: list[int] = []
        # before header level
        for idx in range(1, level):
            numbers.append(level_indexes.setdefault(idx, 1))
        # header level
        index = level_indexes.get(level, 0) + 1
        level_indexes[level] = index
        numbers.append(index)
        # after header level
        idx = level + 1
        while idx in level_indexes:
            del level_indexes[idx]
            idx += 1
        return ".".join(str(x) for x in numbers) + "."

    def fill(
        self,
        document: Document | None = None,
        use_default_styles: bool = True,
    ) -> None:
        """Fill the TOC with titles from the document.

        This method populates the table of contents by scanning the document
        for headers. It is not contextual and will include all titles from
        the document, regardless of their position relative to the TOC.

        If the TOC is not yet part of a document, you must provide one as an
        argument.

        For a well-formatted TOC, it's recommended to leave
        `use_default_styles` as True.

        Args:
            document: The document to scan for titles.
                If not provided, the TOC must already be attached to a
                document.
            use_default_styles: If True, applies default styles to the
                TOC entries.
        """
        # Find the body
        if document is not None:
            body: Element | None = document.body
        else:
            body = self.document_body
        if body is None:
            raise ValueError("The TOC must be related to a document somehow")

        # Save the title
        index_body = self.body
        if index_body is None:
            title = None
        else:
            title = cast(
                Union[None, IndexTitle], index_body.get_element(IndexTitle._tag)
            )

        # Clean the old index-body
        self.body = None  # this ceates a new index_body
        index_body = cast(IndexBody, self.body)

        # Restore the title
        if title and str(title):
            index_body.insert(title, position=0)

        # Insert default TOC style
        if use_default_styles:
            automatic_styles = body.get_element("//office:automatic-styles")
            if isinstance(automatic_styles, Element):  # pragma: nocover
                for level in range(1, 11):
                    if (
                        automatic_styles.get_style(
                            "paragraph", _toc_entry_style_name(level)
                        )
                        is None
                    ):
                        level_style = default_toc_level_style(level)
                        automatic_styles.append(level_style)

        # Auto-fill the index
        outline_level = self.outline_level or 10
        level_indexes: dict[int, int] = {}
        for header in body.headers:
            level = header.get_attribute_integer("text:outline-level") or 0
            if level > outline_level:
                continue
            number_str = self._header_numbering(level_indexes, level)
            # Make the title with "1.2.3. Title" format
            paragraph = Element.from_tag("text:p")
            paragraph.append_plain_text(f"{number_str} {header}")  # type: ignore[attr-defined]
            if use_default_styles:
                paragraph.style = _toc_entry_style_name(level)  # type: ignore[attr-defined]
            index_body.append(paragraph)


TOC._define_attribut_property()


class TocEntryTemplate(Element):
    """Template for a TOC entry, "text:table-of-content-entry-template".

    This element defines the structure for each entry in the table of
    contents, specifying what information is displayed (e.g., chapter number,
    text, page number) and how it is styled.

    Attributes:
        style (str, optional): The style name for the entry.
    """

    _tag = "text:table-of-content-entry-template"
    _properties = (PropDef("style", "text:style-name"),)

    def __init__(
        self,
        style: str | None = None,
        outline_level: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes a TocEntryTemplate element.

        Args:
            style: The style name for the TOC entry.
            outline_level: The outline level this template
                applies to.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if style:
                self.style = style
            if outline_level:
                self.outline_level = outline_level

    @property
    def outline_level(self) -> int | None:
        """The outline level this template applies to."""
        return self.get_attribute_integer("text:outline-level")

    @outline_level.setter
    def outline_level(self, level: int) -> None:
        self.set_attribute("text:outline-level", str(level))

    def complete_defaults(self) -> None:
        """Populates the template with default entry elements.

        This method adds standard elements to the template, such as placeholders
        for chapter number, entry text, and page number, providing a default
        structure for a TOC entry.
        """
        self.append(Element.from_tag("text:index-entry-chapter"))
        self.append(Element.from_tag("text:index-entry-text"))
        self.append(Element.from_tag("text:index-entry-text"))
        ts = Element.from_tag("text:index-entry-text")
        ts.set_style_attribute("style:type", "right")
        ts.set_style_attribute("style:leader-char", ".")
        self.append(ts)
        self.append(Element.from_tag("text:index-entry-page-number"))


TocEntryTemplate._define_attribut_property()


class IndexBody(TocMixin, SectionMixin):
    """Represents the "text:index-body" element, which contains the content of an index.

    This element is used for all types of indexes within an ODF document and
    holds the generated index content.
    """

    _tag: str = "text:index-body"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class IndexTitle(TocMixin, SectionMixin):
    """Represents the title of an index, "text:index-title".

    This element contains the title for an index, and its properties define
    how the title is displayed and protected.

    Attributes:
        name (str): The name of the index title.
        style (str): The style name applied to the index title.
        xml_id (str): A unique XML identifier.
        protected (bool): Indicates if the index title is protected.
        protection_key (str): The protection key if the title is protected.
        protection_key_digest_algorithm (str): The algorithm used for the protection key.
    """

    _tag = "text:index-title"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "text:name"),
        PropDef("style", "text:style-name"),
        PropDef("xml_id", "xml:id"),
        PropDef("protected", "text:protected"),
        PropDef("protection_key", "text:protection-key"),
        PropDef(
            "protection_key_digest_algorithm", "text:protection-key-digest-algorithm"
        ),
    )

    def __init__(
        self,
        name: str | None = None,
        style: str | None = None,
        title_text: str | None = None,
        title_text_style: str | None = None,
        xml_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create an IndexTitle element.

        Args:
            name: The name of the index title.
            style: The style name for the index title.
            title_text: The actual text content of the title.
            title_text_style: The style name for the title text.
            xml_id: A unique XML identifier for the title.
            **kwargs: Arbitrary keyword arguments for the Element base class.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if xml_id:
                self.xml_id = xml_id
            if title_text:
                self.set_title_text(title_text, title_text_style)

    def set_title_text(
        self,
        title_text: str,
        title_text_style: str | None = None,
    ) -> None:
        """Set the actual text content of the index title.

        Args:
            title_text: The text content to set for the title.
            title_text_style: The style name for the title text.
        """
        current = self.get_element("text:p")
        if current:
            current.delete()
        title = Element.from_tag("text:p")
        title.append_plain_text(title_text)  # type: ignore[attr-defined]
        title.style = title_text_style  # type: ignore[attr-defined]
        self.append(title)


IndexTitle._define_attribut_property()


class IndexTitleTemplate(Element):
    """Represents a template style for an index title, "text:index-title-template".

    This element defines the styling for index titles within an ODF document.
    """

    _tag = "text:index-title-template"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("style", "text:style-name"),
    )

    def __init__(self, style: str | None = None, **kwargs: Any) -> None:
        """Create an IndexTitleTemplate element.

        Args:
            style: The style name for the template.
            **kwargs: Arbitrary keyword arguments for the Element base class.
        """
        super().__init__(**kwargs)
        if self._do_init and style:
            self.style = style


IndexTitleTemplate._define_attribut_property()

register_element_class(TocEntryTemplate)
register_element_class(TabStopStyle)
register_element_class(TOC)
register_element_class(IndexBody)
register_element_class(IndexTitle)
register_element_class(IndexTitleTemplate)
