# Copyright 2018-2024 Jérôme Dumonteil
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
"""Document class, root of the ODF document.
"""
from __future__ import annotations

import io
import posixpath
from contextlib import suppress
from copy import deepcopy
from importlib import resources as rso
from mimetypes import guess_type
from operator import itemgetter
from pathlib import Path
from typing import Any
from uuid import uuid4

from .const import (
    ODF_CONTENT,
    ODF_MANIFEST,
    ODF_META,
    ODF_SETTINGS,
    ODF_STYLES,
    ODF_TEMPLATES,
)
from .container import Container
from .content import Content
from .element import Element
from .manifest import Manifest
from .meta import Meta
from .style import Style
from .styles import Styles
from .utils import FAMILY_ODF_STD, bytes_to_str
from .xmlpart import XmlPart

AUTOMATIC_PREFIX = "odfdo_auto_"

UNDERLINE_LVL = ["=", "-", ":", "`", "'", '"', "~", "^", "_", "*", "+"]


def _underline_string(level: int, name: str) -> str:
    """Underline string of the name."""
    if level >= len(UNDERLINE_LVL):
        return "\n"
    return UNDERLINE_LVL[level] * len(name)


def _show_styles(element: Element, level: int = 0) -> str | None:
    output: list[str] = []
    attributes = element.attributes
    children = element.children
    # Don't show the empty elements
    if not attributes and not children:
        return None
    tag_name = element.tag
    output.append(tag_name)
    # Underline the name
    output.append(_underline_string(level, tag_name))
    # Add a separation between name and attributes
    output[-1] += "\n"

    # Attributes
    attrs: list[str] = []
    for key, value in attributes.items():
        attrs.append(f"{key}: {value}")
    if attrs:
        attrs.sort()
        # Add a separation between attributes and children
        attrs[-1] += "\n"
        output.extend(attrs)

    # Children
    # Sort children according to their names
    children2 = [(child.tag, child) for child in children]
    children2.sort()
    children = [child for name, child in children2]
    for child in children:
        child_output = _show_styles(child, level + 1)
        if child_output:
            output.append(child_output)
    return "\n".join(output)


def _get_part_path(path: str) -> str:
    """Transition to real path of XML parts"""
    return {
        "content": ODF_CONTENT,
        "meta": ODF_META,
        "settings": ODF_SETTINGS,
        "styles": ODF_STYLES,
        "manifest": ODF_MANIFEST,
    }.get(path, path)


def _get_part_class(
    path: str,
) -> type[XmlPart] | None:
    return {
        ODF_CONTENT: Content,
        ODF_META: Meta,
        ODF_SETTINGS: XmlPart,
        ODF_STYLES: Styles,
        ODF_MANIFEST: Manifest,
    }.get(path)


def container_from_template(template: str | Path | io.BytesIO) -> Container:
    """Return a Container instance based on template argument.

    Internal use only."""
    template_container = Container()
    if isinstance(template, str) and template in ODF_TEMPLATES:
        template = ODF_TEMPLATES[template]
        with rso.as_file(
            rso.files("odfdo.templates").joinpath(template)
        ) as template_path:
            template_container.open(template_path)
    else:
        # custome template
        template_container.open(template)
    # Return a copy of the template container
    container = template_container.clone
    # Change type from template to regular
    mimetype = container.mimetype.replace("-template", "")
    container.mimetype = mimetype
    # Update the manifest
    manifest = Manifest(ODF_MANIFEST, container)
    manifest.set_media_type("/", mimetype)
    container.set_part(ODF_MANIFEST, manifest.serialize())
    return container


class Document:
    """Abstraction of the ODF document.

    To create a new Document, several possibilities:

        - Document() or Document("text") -> an "empty" document of type text
        - Document("spreadsheet") -> an "empty" document of type spreadsheet
        - Document("presentation") -> an "empty" document of type presentation
        - Document("drawing") -> an "empty" document of type drawing

        Meaning of “empty”: these documents are copies of the default
        templates documents provided with this library, which, as templates,
        are not really empty. It may be useful to clear the newly created
        document: document.body.clear(), or adjust meta informations like
        description or default language: document.meta.set_language('fr-FR')

    If the argument is not a known template type, or is a Path,
    Document(file) will load the content of the ODF file.

    To explicitly create a document from a custom template, use the
    Document.new(path) method whose argument is the path to the template file.
    """

    def __init__(
        self,
        target: str | bytes | Path | Container | io.BytesIO | None = "text",
    ) -> None:
        # Cache of XML parts
        self.__xmlparts: dict[str, XmlPart] = {}
        # Cache of the body
        self.__body: Element | None = None
        self.container: Container | None = None
        if isinstance(target, bytes):
            # eager conversion
            target = bytes_to_str(target)
        if target is None:
            # empty document, you probably don't wnat this.
            self.container = Container()
            return
        if isinstance(target, Path):
            # let's assume we open a container on existing file
            self.container = Container(target)
            return
        if isinstance(target, Container):
            # special internal case, use an existing container
            self.container = target
            return
        if isinstance(target, str):
            if target in ODF_TEMPLATES:
                # assuming a new document from templates
                self.container = container_from_template(target)
                return
            # let's assume we open a container on existing file
            self.container = Container(target)
            return
        if isinstance(target, io.BytesIO):
            self.container = Container(target)
            return
        raise TypeError(f"Unknown Document source type: '{target!r}'")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.get_type()} path={self.path}>"

    def __str__(self) -> str:
        try:
            return str(self.get_formatted_text())
        except NotImplementedError:
            return self.body.text_recursive

    @classmethod
    def new(cls, template: str | Path | io.BytesIO = "text") -> Document:
        """Create a Document from a template.

        The template argument is expected to be the path to a ODF template.

        Arguments:

            template -- str or Path or file-like (io.BytesIO)

        Return : ODF document -- Document
        """
        container = container_from_template(template)
        return cls(container)

    # Public API

    @property
    def path(self) -> Path | None:
        """Shortcut to Document.Container.path."""
        if not self.container:
            return None
        return self.container.path

    @path.setter
    def path(self, path_or_str: str | Path) -> None:
        """Shortcut to Document.Container.path

        Only accepting str or Path."""
        if not self.container:
            return
        self.container.path = Path(path_or_str)

    def get_parts(self) -> list[str]:
        """Return available part names with path inside the archive, e.g.
        ['content.xml', ..., 'Pictures/100000000000032000000258912EB1C3.jpg']
        """
        if not self.container:
            raise ValueError("Empty Container")
        return self.container.get_parts()

    def get_part(self, path: str) -> XmlPart | str | bytes | None:
        """Return the bytes of the given part. The path is relative to the
        archive, e.g. "Pictures/1003200258912EB1C3.jpg".

        'content', 'meta', 'settings', 'styles' and 'manifest' are shortcuts
        to the real path, e.g. content.xml, and return a dedicated object with
        its own API.

        path formated as URI, so always use '/' separator
        """
        if not self.container:
            raise ValueError("Empty Container")
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        # Raw bytes
        if cls is None:
            return self.container.get_part(path)
        # XML part
        part = self.__xmlparts.get(path)
        if part is None:
            self.__xmlparts[path] = part = cls(path, self.container)
        return part

    def set_part(self, path: str, data: bytes) -> None:
        """Set the bytes of the given part. The path is relative to the
        archive, e.g. "Pictures/1003200258912EB1C3.jpg".

        path formated as URI, so always use '/' separator
        """
        if not self.container:
            raise ValueError("Empty Container")
        # "./ObjectReplacements/Object 1"
        path = path.lstrip("./")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        # XML part overwritten
        if cls is not None:
            with suppress(KeyError):
                self.__xmlparts[path]
        self.container.set_part(path, data)

    def del_part(self, path: str) -> None:
        """Mark a part for deletion. The path is relative to the archive,
        e.g. "Pictures/1003200258912EB1C3.jpg"
        """
        if not self.container:
            raise ValueError("Empty Container")
        path = _get_part_path(path)
        cls = _get_part_class(path)
        if path == ODF_MANIFEST or cls is not None:
            raise ValueError(f"part '{path}' is mandatory")
        self.container.del_part(path)

    @property
    def mimetype(self) -> str:
        if not self.container:
            raise ValueError("Empty Container")
        return self.container.mimetype

    @mimetype.setter
    def mimetype(self, mimetype: str) -> None:
        if not self.container:
            raise ValueError("Empty Container")
        self.container.mimetype = mimetype

    def get_type(self) -> str:
        """Get the ODF type (also called class) of this document.

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
    def body(self) -> Element:
        """Return the body element of the content part, where actual content
        is stored.
        """
        if self.__body is None:
            self.__body = self.content.body
        return self.__body

    @property
    def meta(self) -> Meta:
        """Return the meta part (meta.xml) of the document, where meta data
        are stored."""
        metadata = self.get_part(ODF_META)
        if metadata is None or not isinstance(metadata, Meta):
            raise ValueError("Empty Meta")
        return metadata

    @property
    def manifest(self) -> Manifest:
        """Return the manifest part (manifest.xml) of the document."""
        manifest = self.get_part(ODF_MANIFEST)
        if manifest is None or not isinstance(manifest, Manifest):
            raise ValueError("Empty Manifest")
        return manifest

    def _get_formatted_text_footnotes(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Separate text from notes
        if rst_mode:
            result.append("\n")
        else:
            result.append("----\n")
        for citation, body in context["footnotes"]:
            if rst_mode:
                result.append(f".. [#] {body}\n")
            else:
                result.append(f"[{citation}] {body}\n")
        # Append a \n after the notes
        result.append("\n")
        # Reset for the next paragraph
        context["footnotes"] = []

    def _get_formatted_text_annotations(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Insert the annotations
        # With a separation
        if rst_mode:
            result.append("\n")
        else:
            result.append("----\n")
        for annotation in context["annotations"]:
            if rst_mode:
                result.append(f".. [#] {annotation}\n")
            else:
                result.append(f"[*] {annotation}\n")
        context["annotations"] = []

    def _get_formatted_text_images(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Insert the images ref, only in rst mode
        result.append("\n")
        for ref, filename, (width, height) in context["images"]:
            result.append(f".. {ref} image:: {filename}\n")
            if width is not None:
                result.append(f"   :width: {width}\n")
            if height is not None:
                result.append(f"   :height: {height}\n")
        context["images"] = []

    def _get_formatted_text_endnotes(
        self,
        result: list[str],
        context: dict,
        rst_mode: bool,
    ) -> None:
        # Append the end notes
        if rst_mode:
            result.append("\n\n")
        else:
            result.append("\n========\n")
        for citation, body in context["endnotes"]:
            if rst_mode:
                result.append(f".. [*] {body}\n")
            else:
                result.append(f"({citation}) {body}\n")

    def get_formatted_text(self, rst_mode: bool = False) -> str:
        """Return content as text, with some formatting."""
        # For the moment, only "type='text'"
        doc_type = self.get_type()
        if doc_type == "spreadsheet":
            return self._tables_csv()
        if doc_type in {
            "text",
            "text-template",
            "presentation",
            "presentation-template",
        }:
            return self._formatted_text(rst_mode)
        raise NotImplementedError(f"Type of document '{doc_type}' not supported yet")

    def _tables_csv(self) -> str:
        return "\n\n".join(str(table) for table in self.body.get_tables())

    def _formatted_text(self, rst_mode: bool) -> str:
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
        for child in body.children:
            # self._get_formatted_text_child(result, element, context, rst_mode)
            # if child.tag == "table:table":
            #     result.append(child.get_formatted_text(context))
            #     return
            result.append(child.get_formatted_text(context))
            if context["footnotes"]:
                self._get_formatted_text_footnotes(result, context, rst_mode)
            if context["annotations"]:
                self._get_formatted_text_annotations(result, context, rst_mode)
            # Insert the images ref, only in rst mode
            if context["images"]:
                self._get_formatted_text_images(result, context, rst_mode)
        if context["endnotes"]:
            self._get_formatted_text_endnotes(result, context, rst_mode)
        return "".join(result)

    def get_formated_meta(self) -> str:
        """Return meta informations as text, with some formatting."""
        result: list[str] = []

        # Simple values
        def print_info(name: str, value: Any) -> None:
            if value:
                result.append(f"{name}: {value}")

        meta = self.meta
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
        if statistic:
            for name, data in statistic.items():
                result.append(f"  - {name[5:].replace('-', ' ').capitalize()}: {data}")

        # User defined metadata
        result.append("User defined metadata:")
        user_metadata = meta.get_user_defined_metadata()
        for name, data2 in user_metadata.items():
            result.append(f"  - {name}: {data2}")

        # And the description
        print_info("Description", meta.get_description())

        return "\n".join(result) + "\n"

    def add_file(self, path_or_file: str | Path) -> str:
        """Insert a file from a path or a file-like object in the container.

        Return the full path to reference in the content.

        Arguments:

            path_or_file -- str or Path or file-like

        Return: str (URI)
        """
        if not self.container:
            raise ValueError("Empty Container")
        name = ""
        # Folder for added files (FIXME hard-coded and copied)
        manifest = self.manifest
        medias = manifest.get_paths()
        # uuid = str(uuid4())

        if isinstance(path_or_file, (str, Path)):
            path = Path(path_or_file)
            extension = path.suffix.lower()
            name = f"{path.stem}{extension}"
            if posixpath.join("Pictures", name) in medias:
                name = f"{path.stem}_{uuid4()}{extension}"
        else:
            path = None
            name = getattr(path_or_file, "name", None)
            if not name:
                name = str(uuid4())
        media_type, _encoding = guess_type(name)
        if not media_type:
            media_type = "application/octet-stream"
        if manifest.get_media_type("Pictures/") is None:
            manifest.add_full_path("Pictures/")
        full_path = posixpath.join("Pictures", name)
        if path is None:
            self.container.set_part(full_path, path_or_file.read())
        else:
            self.container.set_part(full_path, path.read_bytes())
        manifest.add_full_path(full_path, media_type)
        return full_path

    @property
    def clone(self) -> Document:
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
                if not self.container:
                    raise ValueError("Empty Container")
                setattr(clone, name, self.container.clone)
            else:
                value = deepcopy(getattr(self, name))
                setattr(clone, name, value)
        return clone

    def save(
        self,
        target: str | Path | io.BytesIO | None = None,
        packaging: str = "zip",
        pretty: bool = False,
        backup: bool = False,
    ) -> None:
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
        if not self.container:
            raise ValueError("Empty Container")
        # Some advertising
        self.meta.set_generator_default()
        # Synchronize data with container
        container = self.container
        for path, part in self.__xmlparts.items():
            if part is not None:
                container.set_part(path, part.serialize(pretty))
        # Save the container
        container.save(target, packaging=packaging, backup=backup)

    @property
    def content(self) -> Content:
        content: Content | None = self.get_part(ODF_CONTENT)  # type:ignore
        if content is None:
            raise ValueError("Empty Content")
        return content

    @property
    def styles(self) -> Styles:
        styles: Styles | None = self.get_part(ODF_STYLES)  # type:ignore
        if styles is None:
            raise ValueError("Empty Styles")
        return styles

    # Styles over several parts

    def get_styles(
        self,
        family: str | bytes = "",
        automatic: bool = False,
    ) -> list[Style | Element]:
        # compatibility with old versions:

        if isinstance(family, bytes):
            family = bytes_to_str(family)
        return self.content.get_styles(family=family) + self.styles.get_styles(
            family=family, automatic=automatic
        )

    def get_style(
        self,
        family: str,
        name_or_element: str | Style | None = None,
        display_name: str | None = None,
    ) -> Style | None:
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
        element = self.content.get_style(
            family, name_or_element=name_or_element, display_name=display_name
        )
        if element is not None:
            return element
        # 2. styles.xml
        return self.styles.get_style(
            family,
            name_or_element=name_or_element,
            display_name=display_name,
        )

    @staticmethod
    def _pseudo_style_attribute(style_element: Style | Element, attribute: str) -> Any:
        if hasattr(style_element, attribute):
            return getattr(style_element, attribute)
        return ""

    def _set_automatic_name(self, style: Style, family: str) -> None:
        """Generate a name for the new automatic style."""
        if not hasattr(style, "name"):
            # do nothing
            return
        styles = self.get_styles(family=family, automatic=True)
        max_index = 0
        for existing_style in styles:
            if not hasattr(existing_style, "name"):
                continue
            if not existing_style.name.startswith(AUTOMATIC_PREFIX):
                continue
            try:
                index = int(existing_style.name[len(AUTOMATIC_PREFIX) :])
            except ValueError:
                continue
            max_index = max(max_index, index)

        style.name = f"{AUTOMATIC_PREFIX}{max_index+1}"

    def _insert_style_get_common_styles(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_automatic_styles(
        self,
        style: Style,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.content.get_element("office:automatic-styles")
        # A name ?
        if name:
            if hasattr(style, "name"):
                style.name = name
            existing = self.content.get_style(family, name)
        else:
            self._set_automatic_name(style, family)
            existing = None
        return existing, style_container

    def _insert_style_get_default_styles(
        self,
        style: Style,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:styles")
        style.tag = "style:default-style"
        if name:
            style.del_attribute("style:name")
        existing = self.styles.get_style(family)
        return existing, style_container

    def _insert_style_get_master_page(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:master-styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_font_face_default(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.styles.get_element("office:font-face-decls")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_font_face(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        style_container = self.content.get_element("office:font-face-decls")
        existing = self.content.get_style(family, name)
        return existing, style_container

    def _insert_style_get_page_layout(
        self,
        family: str,
        name: str,
    ) -> tuple[Any, Any]:
        # force to automatic
        style_container = self.styles.get_element("office:automatic-styles")
        existing = self.styles.get_style(family, name)
        return existing, style_container

    def _insert_style_get_draw_fill_image(
        self,
        name: str,
    ) -> tuple[Any, Any]:
        # special case for 'draw:fill-image' pseudo style
        # not family and style_element.__class__.__name__ == "DrawFillImage"
        style_container = self.styles.get_element("office:styles")
        existing = self.styles.get_style("", name)
        return existing, style_container

    def _insert_style_standard(
        self,
        style: Style,
        name: str,
        family: str,
        automatic: bool,
        default: bool,
    ) -> tuple[Any, Any]:
        # Common style
        if name and automatic is False and default is False:
            return self._insert_style_get_common_styles(family, name)
        # Automatic style
        elif automatic is True and default is False:
            return self._insert_style_get_automatic_styles(style, family, name)
        # Default style
        elif automatic is False and default is True:
            return self._insert_style_get_default_styles(style, family, name)
        else:
            raise AttributeError("Invalid combination of arguments")

    def insert_style(  # noqa: C901
        self,
        style: Style | str,
        name: str = "",
        automatic: bool = False,
        default: bool = False,
    ) -> Any:
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

        All styles can't be used as default styles. Default styles are
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
            style_element: Style = Element.from_tag(style)  # type: ignore
        else:
            style_element = style
        if not isinstance(style_element, Element):
            raise TypeError(f"Unknown Style type: '{style!r}'")

        # Get family and name
        family = self._pseudo_style_attribute(style_element, "family")
        if not name:
            name = self._pseudo_style_attribute(style_element, "name")

        # Master page style
        if family == "master-page":
            existing, style_container = self._insert_style_get_master_page(family, name)
        # Font face declarations
        elif family == "font-face":
            if default:
                existing, style_container = self._insert_style_get_font_face_default(
                    family, name
                )
            else:
                existing, style_container = self._insert_style_get_font_face(
                    family, name
                )
        # page layout style
        elif family == "page-layout":
            existing, style_container = self._insert_style_get_page_layout(family, name)
        # Common style
        elif family in FAMILY_ODF_STD or family in {"number"}:
            existing, style_container = self._insert_style_standard(
                style_element, name, family, automatic, default
            )
        elif not family and style_element.__class__.__name__ == "DrawFillImage":
            # special case for 'draw:fill-image' pseudo style
            existing, style_container = self._insert_style_get_draw_fill_image(name)
        # Invalid style
        else:
            raise ValueError(
                "Invalid style: "
                f"{style_element}, tag:{style_element.tag}, family:{family}"
            )

        # Insert it!
        if existing is not None:
            style_container.delete(existing)
        style_container.append(style_element)
        return self._pseudo_style_attribute(style_element, "name")

    def get_styled_elements(self, name: str = "") -> list[Element]:
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- str

        Return: list
        """
        # Header, footer, etc. have styles too
        return self.content.root.get_styled_elements(
            name
        ) + self.styles.root.get_styled_elements(name)

    def show_styles(
        self,
        automatic: bool = True,
        common: bool = True,
        properties: bool = False,
    ) -> str:
        infos = []
        for style in self.get_styles():
            try:
                name = style.name  # type: ignore
            except AttributeError:
                print("--------------")
                print(style.__class__)
                print(style.serialize())
                raise
            if style.__class__.__name__ == "DrawFillImage":
                family = ""
            else:
                family = str(style.family)  # type: ignore
            parent = style.parent
            is_auto = parent and parent.tag == "office:automatic-styles"
            if is_auto and automatic is False or not is_auto and common is False:
                continue
            is_used = bool(self.get_styled_elements(name))
            infos.append(
                {
                    "type": "auto  " if is_auto else "common",
                    "used": "y" if is_used else "n",
                    "family": family,
                    "parent": self._pseudo_style_attribute(style, "parent_style") or "",
                    "name": name or "",
                    "display_name": self._pseudo_style_attribute(style, "display_name")
                    or "",
                    "properties": style.get_properties() if properties else None,  # type: ignore
                }
            )
        if not infos:
            return ""
        # Sort by family and name
        infos.sort(key=itemgetter("family", "name"))
        # Show common and used first
        infos.sort(key=itemgetter("type", "used"), reverse=True)
        max_family = str(max([len(x["family"]) for x in infos]))  # type: ignore
        max_parent = str(max([len(x["parent"]) for x in infos]))  # type: ignore
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
                line += " display_name:" + info["display_name"]  # type: ignore
            output.append(line)
            if info["properties"]:
                for name, value in info["properties"].items():  # type: ignore
                    output.append(f"   - {name}: {value}")
        output.append("")
        return "\n".join(output)

    def delete_styles(self) -> int:
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
        deleted = 0
        for style in self.get_styles():
            if style.name is None:  # type: ignore
                # Don't delete default styles
                continue
            # elif type(style) is odf_master_page:
            #    # Don't suppress header and footer, just styling was removed
            #    continue
            style.delete()
            deleted += 1
        return deleted

    def merge_styles_from(self, document: Document) -> None:
        """Copy all the styles of a document into ourself.

        Styles with the same type and name will be replaced, so only unique
        styles will be preserved.
        """
        manifest = self.manifest
        document_manifest = document.manifest
        for style in document.get_styles():
            tagname = style.tag
            family = self._pseudo_style_attribute(style, "family")
            stylename = style.name  # type: ignore
            container = style.parent
            container_name = container.tag  # type: ignore
            partname = container.parent.tag  # type: ignore
            # The destination part
            if partname == "office:document-styles":
                part: Content | Styles = self.styles
            elif partname == "office:document-content":
                part = self.content
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
            dest = part.get_element(f"//{container_name}")
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
                    url = image.url  # type: ignore
                    part_url = document.get_part(url)
                    # Manually add the part to keep the name
                    self.set_part(url, part_url)  # type: ignore
                    media_type = document_manifest.get_media_type(url)
                    manifest.add_full_path(url, media_type)  # type: ignore
            # Copy images from the fill-image
            elif tagname == "draw:fill-image":
                url = style.url  # type: ignore
                part_url = document.get_part(url)
                self.set_part(url, part_url)  # type: ignore
                media_type = document_manifest.get_media_type(url)
                manifest.add_full_path(url, media_type)  # type: ignore

    def add_page_break_style(self) -> None:
        """Ensure that the document contains the style required for a manual page break.

        Then a manual page break can be added to the document with:
            from paragraph import PageBreak
            ...
            document.body.append(PageBreak())

        Note: this style uses the property 'fo:break-after', another
        possibility could be the property 'fo:break-before'
        """
        if existing := self.get_style(  # noqa: SIM102
            family="paragraph",
            name_or_element="odfdopagebreak",
        ):
            if properties := existing.get_properties():  # noqa: SIM102
                if properties["fo:break-after"] == "page":
                    return
        style = (
            '<style:style style:family="paragraph" style:parent-style-name="Standard" '
            'style:name="odfdopagebreak">'
            '<style:paragraph-properties fo:break-after="page"/></style:style>'
        )
        self.insert_style(style, automatic=False)
