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

from unittest import TestCase, main
from datetime import datetime

from odfdo.document import Document
from odfdo.tracked_changes import TrackedChanges


class TestTrackedChanges(TestCase):
    def setUp(self):
        uri = "samples/tracked_changes.odt"
        self.document = document = Document(uri)
        self.body = document.body

    def test_get_tracked_changes(self):
        tracked_changes = self.body.get_tracked_changes()
        self.assertTrue(isinstance(tracked_changes, TrackedChanges))


class TestChangedRegionTestCase(TestCase):
    def setUp(self):
        uri = "samples/tracked_changes.odt"
        self.document = document = Document(uri)
        self.tracked_changes = document.body.get_tracked_changes()

    def test_get_changed_region_list(self):
        regions = self.tracked_changes.get_changed_regions()
        self.assertEqual(len(regions), 3)

    def test_get_changed_region_list_creator(self):
        creator = "Romain Gauthier"
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_regions(creator=creator)
        expected = (
            '<text:changed-region xml:id="ct140266191788864" text:id="ct140266191788864">\n'
            "  <text:deletion>\n"
            "    <office:change-info>\n"
            "      <dc:creator>Romain Gauthier</dc:creator>\n"
            "      <dc:date>2009-08-21T19:27:00</dc:date>\n"
            "    </office:change-info>\n"
            '    <text:p text:style-name="Standard">les</text:p>\n'
            "  </text:deletion>\n"
            "</text:changed-region>\n"
        )
        self.assertEqual(regions[0].serialize(pretty=True), expected)

    def test_get_changed_region_list_date(self):
        date = datetime(2009, 8, 21, 17, 27, 00)
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_regions(date=date)
        expected = (
            '<text:changed-region xml:id="ct140266193096800" text:id="ct140266193096800">\n'
            "  <text:deletion>\n"
            "    <office:change-info>\n"
            "      <dc:creator>David Versmisse</dc:creator>\n"
            "      <dc:date>2009-08-21T17:27:00</dc:date>\n"
            "    </office:change-info>\n"
            '    <text:p text:style-name="Standard">amis,</text:p>\n'
            "  </text:deletion>\n"
            "</text:changed-region>\n"
        )
        self.assertEqual(regions[0].serialize(pretty=True), expected)

    def test_get_changed_region_list_regex(self):
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_regions(content="amis")
        expected = (
            '<text:changed-region xml:id="ct140266193096800" text:id="ct140266193096800">\n'
            "  <text:deletion>\n"
            "    <office:change-info>\n"
            "      <dc:creator>David Versmisse</dc:creator>\n"
            "      <dc:date>2009-08-21T17:27:00</dc:date>\n"
            "    </office:change-info>\n"
            '    <text:p text:style-name="Standard">amis,</text:p>\n'
            "  </text:deletion>\n"
            "</text:changed-region>\n"
        )
        self.assertEqual(regions[0].serialize(pretty=True), expected)

    def test_get_changed_region_by_id(self):
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(text_id="ct140266193096576")
        self.assertEqual(
            region.serialize(pretty=True),
            (
                '<text:changed-region xml:id="ct140266193096576" text:id="ct140266193096576">\n'
                "  <text:insertion>\n"
                "    <office:change-info>\n"
                "      <dc:creator>Hervé Cauwelier</dc:creator>\n"
                "      <dc:date>2009-08-21T18:27:00</dc:date>\n"
                "    </office:change-info>\n"
                "  </text:insertion>\n"
                "</text:changed-region>\n"
            ),
        )

    def test_get_changed_region_by_creator(self):
        creator = "David Versmisse"
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(creator=creator)
        expected = (
            '<text:changed-region xml:id="ct140266193096800" text:id="ct140266193096800">\n'
            "  <text:deletion>\n"
            "    <office:change-info>\n"
            "      <dc:creator>David Versmisse</dc:creator>\n"
            "      <dc:date>2009-08-21T17:27:00</dc:date>\n"
            "    </office:change-info>\n"
            '    <text:p text:style-name="Standard">amis,</text:p>\n'
            "  </text:deletion>\n"
            "</text:changed-region>\n"
        )
        self.assertEqual(region.serialize(pretty=True), expected)

    def test_get_changed_region_by_date(self):
        date = datetime(2009, 8, 21, 18, 27, 00)
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(date=date)
        self.assertEqual(
            region.serialize(pretty=True),
            (
                '<text:changed-region xml:id="ct140266193096576" text:id="ct140266193096576">\n'
                "  <text:insertion>\n"
                "    <office:change-info>\n"
                "      <dc:creator>Hervé Cauwelier</dc:creator>\n"
                "      <dc:date>2009-08-21T18:27:00</dc:date>\n"
                "    </office:change-info>\n"
                "  </text:insertion>\n"
                "</text:changed-region>\n"
            ),
        )

    def test_get_changed_region_by_content(self):
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(content=r"les")
        expected = (
            '<text:changed-region xml:id="ct140266191788864" text:id="ct140266191788864">\n'
            "  <text:deletion>\n"
            "    <office:change-info>\n"
            "      <dc:creator>Romain Gauthier</dc:creator>\n"
            "      <dc:date>2009-08-21T19:27:00</dc:date>\n"
            "    </office:change-info>\n"
            '    <text:p text:style-name="Standard">les</text:p>\n'
            "  </text:deletion>\n"
            "</text:changed-region>\n"
        )
        self.assertEqual(region.serialize(pretty=True), expected)


class TestChangesIdsTestCase(TestCase):
    def setUp(self):
        uri = "samples/tracked_changes.odt"
        self.document = document = Document(uri)
        self.body = document.body

    def test_get_changes_ids(self):
        paragraph = self.body.get_paragraph(content=r"Bonjour")
        changes_ids = paragraph.get_changes_ids()
        expected = ["ct140266191788864", "ct140266193096576", "ct140266193096800"]
        self.assertEqual(changes_ids, expected)


if __name__ == "__main__":
    main()
