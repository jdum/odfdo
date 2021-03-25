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
"""TOC class for "text:table-of-content" and IndexTitle, TabStopStyle,
IndexTitleTemplate, TocEntryTemplate related classes
"""
from .element import FIRST_CHILD
from .element import register_element_class, Element
from .paragraph import Paragraph
from .style import Style


class IndexTitle(Element):
    """The "text:index-title" element contains the title of an index.

    The element has the following attributes:
    text:name, text:protected, text:protection-key,
    text:protection-key-digest-algorithm, text:style-name, xml:id.

    The actual title is stored in a child element

    Return: IndexTitle
    """

    _tag = "text:index-title"
    _properties = (
        ("name", "text:name"),
        ("style", "text:style-name"),
        ("xml_id", "xml:id"),
        ("protected", "text:protected"),
        ("protection_key", "text:protection-key"),
        ("protection_key_digest_algorithm", "text:protection-key-digest-algorithm"),
    )

    def __init__(
        self,
        name=None,
        style=None,
        title_text=None,
        title_text_style=None,
        xml_id=None,
        **kw,
    ):
        super().__init__(**kw)
        if self._do_init:
            if name:
                self.name = name
            if style:
                self.style = style
            if xml_id:
                self.xml_id = xml_id
            if title_text:
                self.set_title_text(title_text, title_text_style)

    def set_title_text(self, title_text, title_text_style):
        title = Paragraph(title_text, style=title_text_style)
        self.append(title)


IndexTitle._define_attribut_property()

TOC_ENTRY_STYLE_PATTERN = "odfto_toc_level_%s"


class TabStopStyle(Element):
    """ODF "style:tab-stop"
    Base style for a TOC entryBase style for a TOC entry

    Return: TabStopStyle

       9, style:position 19.508.3, style:type 19.515.3.
    """

    _tag = "style:tab-stop"
    _properties = (
        ("style_char", "style:char"),
        ("leader_color", "style:leader-color"),
        ("leader_style", "style:leader-style"),
        ("leader_text", "style:leader-text"),
        ("leader_text_style", "style:leader-text-style"),
        ("leader_type", "style:leader-type"),
        ("leader_width", "style:leader-width"),
        ("style_position", "style:position"),
        ("style_type", "style:type"),
    )

    def __init__(
        self,
        style_char=None,
        leader_color=None,
        leader_style=None,
        leader_text=None,
        leader_text_style=None,
        leader_type=None,
        leader_width=None,
        style_position=None,
        style_type=None,
        **kw,
    ):
        super().__init__(**kw)
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


TabStopStyle._define_attribut_property()


def default_toc_level_style(level):
    """Generate an automatic default style for the given TOC level."""
    tab_stop = TabStopStyle(style_type="right", leader_style="dotted", leader_text=".")
    position = 17.5 - (0.5 * level)
    tab_stop.style_position = f"{position}cm"
    tab_stops = Element.from_tag("style:tab-stops")
    tab_stops.append(tab_stop)
    properties = Element.from_tag("style:paragraph-properties")
    properties.append(tab_stops)
    toc_style_level = Style(
        family="paragraph",
        name=TOC_ENTRY_STYLE_PATTERN % level,
        parent=f"Contents_20_{level}",
    )
    toc_style_level.append(properties)
    return toc_style_level


class TOC(Element):
    """Table of content.
    The "text:table-of-content" element represents a table of contents for a
    document. The items that can be listed in a table of contents are:
      - Headings (as defined by the outline structure of the document), up to
        a selected level.
      - Table of contents index marks.
      - Paragraphs formatted with specified paragraph styles.


    Implementation:
    Default parameters are what most people use: protected from manual
    modifications and not limited in title levels.

    The name is mandatory and derived automatically from the title if not
    given. Provide one in case of a conflict with other TOCs in the same
    document.

    The "text:table-of-content" element has the following attributes:
    text:name, text:protected, text:protection-key,
    text:protection-key-digest-algorithm, text:style-name and xml:id.

    Arguments:

        title -- str

        name -- str

        protected -- bool

        outline_level -- int

        style -- str

        title_style -- str

        entry_style -- str

    Return: TOC
    """

    _tag = "text:table-of-content"
    _properties = (
        ("name", "text:name"),
        ("style", "text:style-name"),
        ("xml_id", "xml:id"),
        ("protected", "text:protected"),
        ("protection_key", "text:protection-key"),
        ("protection_key_digest_algorithm", "text:protection-key-digest-algorithm"),
    )

    def __init__(
        self,
        title="Table of Contents",
        name=None,
        protected=True,
        outline_level=None,
        style=None,
        title_style="Contents_20_Heading",
        entry_style="Contents_20_%d",
        **kw,
    ):
        super().__init__(**kw)
        if self._do_init:
            if style:
                self.style = style
            if protected:
                self.protected = protected
            if name is None:
                name = "%s1" % title
                self.name = name
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
    def create_toc_source(title, outline_level, title_style, entry_style):
        toc_source = Element.from_tag("text:table-of-content-source")
        toc_source.set_attribute("text:outline-level", outline_level)
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

    def get_formatted_text(self, context):
        index_body = self.get_element("text:index-body")

        if index_body is None:
            return ""

        if context["rst_mode"]:
            return "\n.. contents::\n\n"

        result = []
        for element in index_body.children:
            if element.tag == "text:index-title":
                for e in element.children:
                    result.append(e.get_formatted_text(context))
                result.append("\n")
            else:
                result.append(element.get_formatted_text(context))
        result.append("\n")
        return "".join(result)

    @property
    def outline_level(self):
        source = self.get_element("text:table-of-content-source")
        if source is None:
            return None
        return source.get_attribute_integer("text:outline-level")

    @outline_level.setter
    def outline_level(self, level):
        source = self.get_element("text:table-of-content-source")
        if source is None:
            source = Element.from_tag("text:table-of-content-source")
            self.insert(source, FIRST_CHILD)
        source.set_attribute("text:outline-level", level)

    @property
    def body(self):
        return self.get_element("text:index-body")

    @body.setter
    def body(self, body=None):
        old_body = self.body
        if old_body is not None:
            self.delete(old_body)
        if body is None:
            body = Element.from_tag("text:index-body")
        self.append(body)
        return body

    def get_title(self):
        index_body = self.body
        if index_body is None:
            return None
        index_title = index_body.get_element(IndexTitle._tag)
        if index_title is None:
            return None
        return index_title.text_content

    def set_toc_title(self, title, style=None, text_style=None):
        index_body = self.body
        if index_body is None:
            self.body = None
            index_body = self.body
        index_title = index_body.get_element(IndexTitle._tag)
        if index_title is None:
            name = "%s_Head" % self.name
            index_title = IndexTitle(
                name=name, style=style, title_text=title, text_style=text_style
            )
            index_body.append(index_title)
        else:
            if style:
                index_title.style = style
            paragraph = index_title.get_paragraph()
            if paragraph is None:
                paragraph = Paragraph()
                index_title.append(paragraph)
            if text_style:
                paragraph.style = text_style
            paragraph.text = title

    def fill(self, document=None, use_default_styles=True):
        """Fill the TOC with the titles found in the document. A TOC is not
        contextual so it will catch all titles before and after its insertion.
        If the TOC is not attached to a document, attach it beforehand or
        provide one as argument.

        For having a pretty TOC, let use_default_styles by default.

        Arguments:

            document -- Document

            use_default_styles -- bool
        """
        # Find the body
        if document is not None:
            body = document.body
        else:
            body = self.document_body
        if body is None:
            raise ValueError("the TOC must be related to a document somehow")

        # Save the title
        index_body = self.body
        title = index_body.get_element("text:index-title")

        # Clean the old index-body
        self.body = None
        index_body = self.body

        # Restore the title
        index_body.insert(title, position=0)

        # Insert default TOC style
        if use_default_styles:
            automatic_styles = body.get_element("//office:automatic-styles")
            for level in range(1, 11):
                if (
                    automatic_styles.get_style(
                        "paragraph", TOC_ENTRY_STYLE_PATTERN % level
                    )
                    is None
                ):
                    level_style = default_toc_level_style(level)
                    automatic_styles.append(level_style)

        # Auto-fill the index
        outline_level = self.outline_level or 10
        level_indexes = {}
        for header in body.get_headers():
            level = header.get_attribute_integer("text:outline-level")
            if level is None or level > outline_level:
                continue
            number = []
            # 1. l < level
            for l in range(1, level):
                index = level_indexes.setdefault(l, 1)
                number.append(str(index))
            # 2. l == level
            index = level_indexes.setdefault(level, 0) + 1
            level_indexes[level] = index
            number.append(str(index))
            # 3. l > level
            for l in range(level + 1, 11):
                if l in level_indexes:
                    del level_indexes[l]
            number = ".".join(number) + "."
            # Make the title with "1.2.3. Title" format
            title = "%s %s" % (number, header.text)
            paragraph = Paragraph(title)
            if use_default_styles:
                paragraph.style = TOC_ENTRY_STYLE_PATTERN % level
            index_body.append(paragraph)


TOC._define_attribut_property()


class IndexTitleTemplate(Element):
    """ODF "text:index-title-template"

    Arguments:

        style -- str

    Return: IndexTitleTemplate
    """

    _tag = "text:index-title-template"
    _properties = (("style", "text:style-name"),)

    def __init__(self, style=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if style:
                self.style = style


IndexTitleTemplate._define_attribut_property()


class TocEntryTemplate(Element):
    """ODF "text:table-of-content-entry-template"

    Arguments:

        style -- str

    Return: TocEntryTemplate
    """

    _tag = "text:table-of-content-entry-template"
    _properties = (("style", "text:style-name"),)

    def __init__(self, style=None, outline_level=None, **kw):
        super().__init__(**kw)
        if self._do_init:
            if style:
                self.style = style
            if outline_level:
                self.outline_level = outline_level

    @property
    def outline_level(self):
        return self.get_attribute_integer("text:outline-level")

    @outline_level.setter
    def outline_level(self, level):
        self.set_attribute("text:outline-level", level)

    def complete_defaults(self):
        self.append(Element.from_tag("text:index-entry-chapter"))
        self.append(Element.from_tag("text:index-entry-text"))
        self.append(Element.from_tag("text:index-entry-text"))
        ts = Element.from_tag("text:index-entry-text")
        ts.set_style_attribute("style:type", "right")
        ts.set_style_attribute("style:leader-char", ".")
        self.append(ts)
        self.append(Element.from_tag("text:index-entry-page-number"))


TocEntryTemplate._define_attribut_property()

register_element_class(IndexTitle)
register_element_class(IndexTitleTemplate)
register_element_class(TocEntryTemplate)
register_element_class(TabStopStyle)
register_element_class(TOC)
