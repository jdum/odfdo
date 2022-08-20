#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

from unittest import TestLoader, TestSuite, TextTestRunner

import test_bookmark
import test_container
import test_content
import test_datatype
import test_document
import test_draw_page
import test_element
import test_frame
import test_header
import test_image
import test_link
import test_list
import test_manifest
import test_meta
import test_note
import test_paragraph
import test_reference
import test_section
import test_shapes
import test_span
import test_style
import test_styles
import test_table
import test_text
import test_toc
import test_tracked_changes
import test_utils
import test_variable
import test_xmlpart

test_modules = [
    test_bookmark,
    test_container,
    test_content,
    test_datatype,
    test_document,
    test_draw_page,
    test_element,
    test_frame,
    test_header,
    test_image,
    test_link,
    test_list,
    test_manifest,
    test_meta,
    test_note,
    test_paragraph,
    test_reference,
    test_section,
    test_shapes,
    test_span,
    test_style,
    test_styles,
    test_table,
    test_text,
    test_toc,
    test_tracked_changes,
    test_utils,
    test_variable,
    test_xmlpart,
]

loader = TestLoader()

if __name__ == "__main__":
    suite = TestSuite()
    for module in test_modules:
        suite.addTest(loader.loadTestsFromModule(module))

    TextTestRunner(verbosity=1).run(suite)
