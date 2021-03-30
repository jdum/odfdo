# Copyright 2018-2020 Jérôme Dumonteil
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Document class, root of the ODF document
"""
import os
import posixpath
from copy import deepcopy
from mimetypes import guess_type
from operator import itemgetter
from uuid import uuid4

from .const import (
    ODF_CONTENT,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEMPLATES,
    ODF_MANIFEST,
)
from .container import Container
from .content import Content
from .element import Element
from .manifest import Manifest
from .meta import Meta

# from .style import registered_styles
from .styles import Styles

# from utils import obsolete
from .xmlpart import XmlPart
from .utils import to_str, FAMILY_ODF_STD

underline_lvl = ["=", "-", ":", "`", "'", '"', "~", "^", "_", "*", "+"]


def _show_styles(element, level=0):
    output = []
    attributes = element.attributes
    children = element.children
    # Don't show the empty elements
    if not attributes and not children:
        return None
    tag_name = element.tag
    output.append(tag_name)
    # Underline and Overline the name
    underline = underline_lvl[level] * len(tag_name)
    underline = underline if level < len(underline_lvl) else "\n"
    output.append(underline)
    # Add a separation between name and attributes
    output[-1] += "\n"
    attrs = []
    # Attributes
    for key, value in attributes.items():
        attrs.append("%s: %s" % (key, value))
    if attrs:
        attrs.sort()
        # Add a separation between attributes and children
        attrs[-1] += "\n"
        output.extend(attrs)
    # Children
    # Sort children according to their names
    children = [(child.tag, child) for child in children]
    children.sort()
    children = [child for name, child in children]
    for child in children:
        child_output = _show_styles(child, level + 1)
        if child_output:
            output.append(child_output)
    return "\n".join(output)


# Transition to real path of XML parts
def _get_part_path(path):
    return {
        "content": ODF_CONTENT,
        "meta": ODF_META,
        "settings": ODF_SETTINGS,
        "styles": ODF_STYLES,
        "manifest": ODF_MANIFEST,
    }.get(path, path)


def _get_part_class(path):
    return {
        ODF_CONTENT: Content,
        ODF_META: Meta,
        ODF_SETTINGS: XmlPart,
        ODF_STYLES: Styles,
        ODF_MANIFEST: Manifest,
    }.get(path)


class Document:
    """Abstraction of the ODF document."""

    def __init__(self, target="text"):
        # Cache of XML parts
        self.__xmlparts = {}
        # Cache of the body
        self.__body = None
        self.container = None
        if target is None:
            # empty document
            self.container = Container()
            return
        if isinstance(target, Container):
            self.container = target
            return
        if to_str(target) in ODF_TEMPLATES:
            # assuming a new document from templates
            self.container = Container.new(target)
            return
        # let's assume we open a container on existing file
        self.container = Container()
        self.container.open(target)

    @classmethod
    def new(cls, target="text"):
        doc = Document()
        doc.container = Container.new(target)
        return doc

    # Public API

    def get_parts(self):
        """Return available part names with path inside the archive, e.g.
        ['content.xml', ..., 'Pictures/100000000000032000000258912EB1C3.jpg']
        """
        return self.container.get_parts()

    def get_part(self, path):
        """Return the bytes of the given part. The path is relative to the
        archive, e.g. "Pictures/1003200258912EB1C3.jpg".

        'content', 'meta', 'settings', 'styles' and 'manifest' are shortcuts
        to the real path, e.g. content.xml, and return a dedicated object with
        its own API.

        path formated as URI, so always use '/' separator
        """
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        container = self.container
        # Raw bytes
        if cls is None:
            return container.get_part(path)
        # XML part
        xmlparts = self.__xmlparts
        part = xmlparts.get(path)
        if part is None:
            xmlparts[path] = part = cls(path, container)
        return part

    def set_part(self, path, data):
        """Set the bytes of the given part. The path is relative to the
        archive, e.g. "Pictures/1003200258912EB1C3.jpg".

        path formated as URI, so always use '/' separator
        """
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        # XML part overwritten
        if cls is not None:
            del self.__xmlparts[path]
        return self.container.set_part(path, data)

    def del_part(self, path):
        """Mark a part for deletion. The path is relative to the archive,
        e.g. "Pictures/1003200258912EB1C3.jpg"
        """
        path = _get_part_path(path)
        cls = _get_part_class(path)
        if path == ODF_MANIFEST or cls is not None:
            raise ValueError('part "%s" is mandatory' % path)
        return self.container.del_part(path)

    @property
    def mimetype(self):
        return self.container.mimetype

    @mimetype.setter
    def mimetype(self, m):
        self.container.mimetype = m

    def get_type(self):
        """
        Get the ODF type (also called class) of this document.

        Return: 'chart', 'database', 'formula', 'graphics',
            'graphics-template', 'image', 'presentation',
            'presentation-template', 'spreadsheet', 'spreadsheet-template',
            'text', 'text-master', 'text-template' or 'text-web'
        """
        # The mimetype must be with the form:
        # application/vnd.oasis.opendocument.text

        # Isolate and return the last part
        return self.mimetype.rsplit(".", 1)[-1]

    @property
    def body(self):
        """Return the body element of the content part, where actual content
        is stored.
        """
        if self.__body is None:
            content = self.get_part(ODF_CONTENT)
            self.__body = content.body
        return self.__body

    def get_formatted_text(self, rst_mode=False):
        """Return content as text, with some formatting."""
        # For the moment, only "type='text'"
        doc_type = self.get_type()
        if doc_type not in {
            "text",
            "text-template",
            "presentation",
            "presentation-template",
        }:
            raise NotImplementedError(
                'Type of document "%s" not ' "supported yet" % doc_type
            )
        # Initialize an empty context
        context = {
            "document": self,
            "footnotes": [],
            "endnotes": [],
            "annotations": [],
            "rst_mode": rst_mode,
            "img_counter": 0,
            "images": [],
            "no_img_level": 0,
        }
        body = self.body
        # Get the text
        result = []
        for element in body.children:
            if element.tag == "table:table":
                result.append(element.get_formatted_text(context))
            else:
                result.append(element.get_formatted_text(context))
                # Insert the notes
                footnotes = context["footnotes"]
                # Separate text from notes
                if footnotes:
                    if rst_mode:
                        result.append("\n")
                    else:
                        result.append("----\n")
                    for citation, body in footnotes:
                        if rst_mode:
                            result.append(".. [#] %s\n" % body)
                        else:
                            result.append("[%s] %s\n" % (citation, body))
                    # Append a \n after the notes
                    result.append("\n")
                    # Reset for the next paragraph
                    context["footnotes"] = []
                # Insert the annotations
                annotations = context["annotations"]
                # With a separation
                if annotations:
                    if rst_mode:
                        result.append("\n")
                    else:
                        result.append("----\n")
                    for annotation in annotations:
                        if rst_mode:
                            result.append(".. [#] %s\n" % annotation)
                        else:
                            result.append("[*] %s\n" % annotation)
                    context["annotations"] = []
                # Insert the images ref, only in rst mode
                images = context["images"]
                if images:
                    result.append("\n")
                    for ref, filename, (width, height) in images:
                        result.append(".. %s image:: %s\n" % (ref, filename))
                        if width is not None:
                            result.append("   :width: %s\n" % width)
                        if height is not None:
                            result.append("   :height: %s\n" % height)
                        result.append("\n")
                    context["images"] = []
        # Append the end notes
        endnotes = context["endnotes"]
        if endnotes:
            if rst_mode:
                result.append("\n\n")
            else:
                result.append("\n========\n")
            for citation, body in endnotes:
                if rst_mode:
                    result.append(".. [*] %s\n" % body)
                else:
                    result.append("(%s) %s\n" % (citation, body))
        return "".join(result)

    def get_formated_meta(self):
        """Return meta informations as text, with some formatting."""
        result = []

        meta = self.get_part(ODF_META)

        # Simple values
        def print_info(name, value):
            if value:
                result.append("%s: %s" % (name, value))

        print_info("Title", meta.get_title())
        print_info("Subject", meta.get_subject())
        print_info("Language", meta.get_language())
        print_info("Modification date", meta.get_modification_date())
        print_info("Creation date", meta.get_creation_date())
        print_info("Initial creator", meta.get_initial_creator())
        print_info("Keyword", meta.get_keywords())
        print_info("Editing duration", meta.get_editing_duration())
        print_info("Editing cycles", meta.get_editing_cycles())
        print_info("Generator", meta.get_generator())

        # Statistic
        result.append("Statistic:")
        statistic = meta.get_statistic()
        for name, value in statistic.items():
            result.append(
                "  - %s: %s" % (name[5:].replace("-", " ").capitalize(), value)
            )

        # User defined metadata
        result.append("User defined metadata:")
        user_metadata = meta.get_user_defined_metadata()
        for name, value in user_metadata.items():
            result.append("  - %s: %s" % (name, value))

        # And the description
        print_info("Description", meta.get_description())

        return "\n".join(result) + "\n"

    def add_file(self, path_or_file):
        """Insert a file from a path or a fike-like object in the container.
        Return the full path to reference it in the content.

        Arguments:

            path_or_file -- str or file-like

        Return: str (URI)
        """
        name = None
        close_after = False
        # Folder for added files (FIXME hard-coded and copied)
        manifest = self.get_part(ODF_MANIFEST)
        medias = manifest.get_paths()

        if isinstance(path_or_file, str):
            handler = open(path_or_file, "rb")
            name = path_or_file
            close_after = True
        else:
            handler = path_or_file
            name = getattr(path_or_file, "name", None)
        name = os.path.basename(name)
        # Generate a safe portable name
        uuid = str(uuid4())
        if name is None:
            name = uuid
            media_type = ""
        else:
            root, extension = os.path.splitext(name)
            extension = extension.lower()
            name = root + extension
            media_type, _encoding = guess_type(name)
            # Check this name is already used in the document
            if posixpath.join("Pictures", name) in medias:
                root = "%s_%s" % (root, uuid)
                name = root + extension
                media_type, _encoding = guess_type(name)

        if manifest.get_media_type("Pictures/") is None:
            manifest.add_full_path("Pictures/")

        full_path = posixpath.join("Pictures", name)
        self.container.set_part(full_path, handler.read())

        # Update manifest
        manifest.add_full_path(full_path, media_type)
        # Close file
        if close_after:
            handler.close()
        return full_path

    @property
    def clone(self):
        """Return an exact copy of the document.

        Return: Document
        """
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == "_Document__body":
                setattr(clone, name, None)
            elif name == "_Document__xmlparts":
                setattr(clone, name, {})
            elif name == "container":
                setattr(clone, name, self.container.clone)
            else:
                value = deepcopy(getattr(self, name))
                setattr(clone, name, value)
        return clone

    def save(self, target=None, packaging=None, pretty=False, backup=False):
        """Save the document, at the same place it was opened or at the given
        target path. Target can also be a file-like object. It can be saved
        as a Zip file (default) or as files in a folder (for debugging
        purpose). XML parts can be pretty printed.

        Arguments:

            target -- str or file-like object

            packaging -- 'zip' or 'folder'

            pretty -- bool

            backup -- bool
        """
        # Some advertising
        meta = self.get_part(ODF_META)
        meta.set_generator_default()
        # Synchronize data with container
        container = self.container
        for path, part in self.__xmlparts.items():
            if part is not None:
                container.set_part(path, part.serialize(pretty))
        # Save the container
        container.save(target, packaging=packaging, backup=backup)

    # Styles over several parts

    def get_styles(self, family=None, automatic=False):
        content = self.get_part(ODF_CONTENT)
        styles = self.get_part(ODF_STYLES)
        family = to_str(family)
        return content.get_styles(family=family) + styles.get_styles(
            family=family, automatic=automatic
        )

    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in a
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            name -- str or Element or None

            display_name -- str

        Return: Style or None if not found.
        """
        # 1. content.xml
        family = to_str(family)
        content = self.get_part(ODF_CONTENT)
        element = content.get_style(
            family, name_or_element=name_or_element, display_name=display_name
        )
        if element is not None:
            return element
        # 2. styles.xml
        styles = self.get_part(ODF_STYLES)
        return styles.get_style(
            family, name_or_element=name_or_element, display_name=display_name
        )

    def insert_style(self, style, name=None, automatic=False, default=False):
        """Insert the given style object in the document, as required by the
        style family and type.

        The style is expected to be a common style with a name. In case it
        was created with no name, the given can be set on the fly.

        If automatic is True, the style will be inserted as an automatic
        style.

        If default is True, the style will be inserted as a default style and
        would replace any existing default style of the same family. Any name
        or display name would be ignored.

        Automatic and default arguments are mutually exclusive.

        All styles can’t be used as default styles. Default styles are
        allowed for the following families: paragraph, text, section, table,
        table-column, table-row, table-cell, table-page, chart, drawing-page,
        graphic, presentation, control and ruby.

        Arguments:

            style -- Style or str

            name -- str

            automatic -- bool

            default -- bool

        Return : style name -- str
        """

        # if style is a str, assume it is the Style definition
        if isinstance(style, str):
            style = Element.from_tag(style)

        # Get family and name
        family = style.family

        if name is None:
            name = style.name

        # Master page style
        if family == "master-page":
            part = self.get_part(ODF_STYLES)
            container = part.get_element("office:master-styles")
            existing = part.get_style(family, name)
        # Font face declarations
        elif family == "font-face":
            if default:
                part = self.get_part(ODF_STYLES)
            else:
                part = self.get_part(ODF_CONTENT)
            container = part.get_element("office:font-face-decls")
            existing = part.get_style(family, name)
        # page layout style
        elif family == "page-layout":
            part = self.get_part(ODF_STYLES)
            # force to automatic
            container = part.get_element("office:automatic-styles")
            existing = part.get_style(family, name)
        # Common style
        elif family in FAMILY_ODF_STD or family in {"number"}:
            # Common style
            if name and automatic is False and default is False:
                part = self.get_part(ODF_STYLES)
                container = part.get_element("office:styles")
                existing = part.get_style(family, name)

            # Automatic style
            elif automatic is True and default is False:
                part = self.get_part(ODF_CONTENT)
                container = part.get_element("office:automatic-styles")

                # A name ?
                if name is None:
                    # Make a beautiful name

                    # TODO: Use prefixes of Ooo: Mpm1, ...
                    prefix = "lpod_auto_"

                    styles = self.get_styles(family=family, automatic=True)
                    names = [s.name for s in styles]
                    numbers = [
                        int(name[len(prefix) :])
                        for name in names
                        if name and name.startswith(prefix)
                    ]
                    if numbers:
                        number = max(numbers) + 1
                    else:
                        number = 1
                    name = prefix + str(number)

                    # And set it
                    style.name = name
                    existing = None
                else:
                    existing = part.get_style(family, name)
                    style.name = name

            # Default style
            elif automatic is False and default is True:
                part = self.get_part(ODF_STYLES)
                container = part.get_element("office:styles")

                # Force default style
                style.tag = "style:default-style"
                if name is not None:
                    style.del_attribute("style:name")

                existing = part.get_style(family)

            # Error
            else:
                raise AttributeError("invalid combination of arguments")
        # Invalid style
        else:
            raise ValueError(
                f"invalid style: {style}, tag:{style.tag}, family:{family}"
            )

        # Insert it!
        if existing is not None:
            container.delete(existing)
        container.append(style)
        return style.name

    def get_styled_elements(self, name=True):
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- str

        Return: list
        """
        content = self.get_part(ODF_CONTENT)
        # Header, footer, etc. have styles too
        styles = self.get_part(ODF_STYLES)
        return content.root.get_styled_elements(name) + styles.root.get_styled_elements(
            name
        )

    def show_styles(self, automatic=True, common=True, properties=False):
        infos = []
        for style in self.get_styles():
            try:
                name = style.name
            except AttributeError:
                print("--------------")
                print(style.__class__)
                print(style.serialize())
                raise
            parent = style.parent
            is_auto = parent and parent.tag == "office:automatic-styles"
            if is_auto and automatic is False or not is_auto and common is False:
                continue
            is_used = bool(self.get_styled_elements(name))
            infos.append(
                {
                    "type": "auto  " if is_auto else "common",
                    "used": "y" if is_used else "n",
                    "family": style.family or "",
                    "parent": style.parent_style or "",
                    "name": name or "",
                    "display_name": style.display_name,
                    "properties": style.get_properties() if properties else None,
                }
            )
        if not infos:
            return ""
        # Sort by family and name
        infos.sort(key=itemgetter("family", "name"))
        # Show common and used first
        infos.sort(key=itemgetter("type", "used"), reverse=True)
        max_family = str(max([len(x["family"]) for x in infos]))
        max_parent = str(max([len(x["parent"]) for x in infos]))
        formater = (
            "%(type)s used:%(used)s family:%(family)-0"
            + max_family
            + "s parent:%(parent)-0"
            + max_parent
            + "s name:%(name)s"
        )
        output = []
        for info in infos:
            line = formater % info
            if info["display_name"]:
                line += " display_name:" + info["display_name"]
            output.append(line)
            if info["properties"]:
                for name, value in info["properties"].items():
                    output.append("   - %s: %s" % (name, value))
        output.append("")
        return "\n".join(output)

    def delete_styles(self):
        """Remove all style information from content and all styles.

        Return: number of deleted styles
        """
        # First remove references to styles
        for element in self.get_styled_elements():
            for attribute in (
                "text:style-name",
                "draw:style-name",
                "draw:text-style-name",
                "table:style-name",
                "style:page-layout-name",
            ):
                try:
                    element.del_attribute(attribute)
                except KeyError:
                    continue
        # Then remove supposedly orphaned styles
        i = 0
        for style in self.get_styles():
            if style.name is None:
                # Don't delete default styles
                continue
            # elif type(style) is odf_master_page:
            #    # Don't suppress header and footer, just styling was removed
            #    continue
            style.delete()
            i += 1
        return i

    def merge_styles_from(self, document):
        """Copy all the styles of a document into ourself.

        Styles with the same type and name will be replaced, so only unique
        styles will be preserved.
        """
        styles = self.get_part(ODF_STYLES)
        content = self.get_part(ODF_CONTENT)
        manifest = self.get_part(ODF_MANIFEST)
        document_manifest = document.get_part(ODF_MANIFEST)
        for style in document.get_styles():
            tagname = style.tag
            family = style.family
            stylename = style.name
            container = style.parent
            container_name = container.tag
            partname = container.parent.tag
            # The destination part
            if partname == "office:document-styles":
                part = styles
            elif partname == "office:document-content":
                part = content
            else:
                raise NotImplementedError(partname)
            # Implemented containers
            if container_name not in {
                "office:styles",
                "office:automatic-styles",
                "office:master-styles",
                "office:font-face-decls",
            }:
                raise NotImplementedError(container_name)
            dest = part.get_element("//%s" % container_name)
            # Implemented style types
            # if tagname not in registered_styles:
            #    raise NotImplementedError(tagname)
            duplicate = part.get_style(family, stylename)
            if duplicate is not None:
                duplicate.delete()
            dest.append(style)
            # Copy images from the header/footer
            if tagname == "style:master-page":
                query = "descendant::draw:image"
                for image in style.get_elements(query):
                    url = image.get_url()
                    part = document.get_part(url)
                    # Manually add the part to keep the name
                    self.set_part(url, part)
                    media_type = document_manifest.get_media_type(url)
                    manifest.add_full_path(url, media_type)
            # Copy images from the fill-image
            elif tagname == "draw:fill-image":
                url = style.get_url()
                part = document.get_part(url)
                self.set_part(url, part)
                media_type = document_manifest.get_media_type(url)
                manifest.add_full_path(url, media_type)
