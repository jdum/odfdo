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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""Style-related constants and mappings for ODF documents.

This module defines constants and dictionaries that map style family names
to their corresponding ODF tag names, as specified in the ODF 1.2 standard.
It is used internally to manage and register different types of styles.
"""

from __future__ import annotations

# style:family as defined by ODF 1.2, e.g. xxx possibily for:
# 'style:style style:family="xxx"'
FAMILY_ODF_STD = {
    "chart",
    "drawing-page",
    "graphic",
    "paragraph",
    "presentation",
    "ruby",
    "section",
    "table",
    "table-cell",
    "table-column",
    "table-row",
    "text",
}

_BASE_FAMILY_MAP = {k: "style:style" for k in FAMILY_ODF_STD}  # noqa:C420

_FALSE_FAMILY_MAP = {
    "background-image": "style:background-image",
    "date": "number:date-style",
    "font-face": "style:font-face",
    "list": "text:list-style",
    "marker": "draw:marker",
    "number": "number:number-style",
    "outline": "text:outline-style",
    "page-layout": "style:page-layout",
    "percentage": "number:percentage-style",
    "presentation-page-layout": "style:presentation-page-layout",
    "time": "number:time-style",
    "boolean": "number:boolean-style",
    "currency": "number:currency-style",
    "master-page": "style:master-page",
}
# "tab-stop": "style:tab-stop", Defined in toc.py
# "master-page": "style:master-page",


OTHER_STYLES = {
    "style:default-style",
    "style:footer-style",
    "style:header-style",
    "text:list-level-style-bullet",
    "text:list-level-style-image",
    "text:list-level-style-number",
}

SUBCLASS_STYLES = {"background-image"}

FAMILY_MAPPING = {**_BASE_FAMILY_MAP, **_FALSE_FAMILY_MAP}

FALSE_FAMILY_MAP_REVERSE = {v: k for k, v in _FALSE_FAMILY_MAP.items()}
SUBCLASSED_STYLES = {"style:background-image", "style:master-page", "style:page-layout"}
STYLES_TO_REGISTER = (set(FAMILY_MAPPING.values()) | OTHER_STYLES) - SUBCLASSED_STYLES
