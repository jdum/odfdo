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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

from collections import namedtuple
from collections.abc import Iterable
from datetime import datetime

import pytest

from odfdo.document import Document
from odfdo.tracked_changes import TrackedChanges

Sample = namedtuple("Sample", ["doc", "changes"])


@pytest.fixture
def sample(samples) -> Iterable[Sample]:
    document = Document(samples("tracked_changes.odt"))
    yield Sample(doc=document, changes=document.body.get_tracked_changes())


def test_instance_tracked_changes(sample):
    assert isinstance(sample.changes, TrackedChanges)


def test_tracked_changes_property(sample, samples):
    document2 = Document(samples("tracked_changes.odt"))
    sample2 = Sample(doc=document2, changes=document2.body.tracked_changes)
    assert isinstance(sample2.changes, TrackedChanges)
    assert sample.changes.serialize() == sample2.changes.serialize()


def test_get_changed_region_list(sample):
    regions = sample.changes.get_changed_regions()
    assert len(regions) == 3


def test_get_changed_region_list_creator(sample):
    creator = "Romain Gauthier"
    tracked_changes = sample.changes
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
    assert regions[0].serialize(pretty=True) == expected


def test_get_changed_region_list_date(sample):
    date = datetime(2009, 8, 21, 17, 27, 00)
    tracked_changes = sample.changes
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
    assert regions[0].serialize(pretty=True) == expected


def test_get_changed_region_list_regex(sample):
    tracked_changes = sample.changes
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
    assert regions[0].serialize(pretty=True) == expected


def test_get_changed_region_by_id(sample):
    tracked_changes = sample.changes
    region = tracked_changes.get_changed_region(text_id="ct140266193096576")
    expected = (
        '<text:changed-region xml:id="ct140266193096576" text:id="ct140266193096576">\n'
        "  <text:insertion>\n"
        "    <office:change-info>\n"
        "      <dc:creator>Hervé Cauwelier</dc:creator>\n"
        "      <dc:date>2009-08-21T18:27:00</dc:date>\n"
        "    </office:change-info>\n"
        "  </text:insertion>\n"
        "</text:changed-region>\n"
    )
    assert region.serialize(pretty=True) == expected


def test_get_changed_region_by_creator(sample):
    creator = "David Versmisse"
    tracked_changes = sample.changes
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
    assert region.serialize(pretty=True) == expected


def test_get_changed_region_by_date(sample):
    date = datetime(2009, 8, 21, 18, 27, 00)
    tracked_changes = sample.changes
    region = tracked_changes.get_changed_region(date=date)
    expected = (
        '<text:changed-region xml:id="ct140266193096576" text:id="ct140266193096576">\n'
        "  <text:insertion>\n"
        "    <office:change-info>\n"
        "      <dc:creator>Hervé Cauwelier</dc:creator>\n"
        "      <dc:date>2009-08-21T18:27:00</dc:date>\n"
        "    </office:change-info>\n"
        "  </text:insertion>\n"
        "</text:changed-region>\n"
    )
    assert region.serialize(pretty=True) == expected


def test_get_changed_region_by_content(sample):
    tracked_changes = sample.changes
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
    assert region.serialize(pretty=True) == expected


def test_get_changes_ids(sample):
    paragraph = sample.doc.body.get_paragraph(content=r"Bonjour")
    changes_ids = paragraph.get_changes_ids()
    expected = ["ct140266191788864", "ct140266193096576", "ct140266193096800"]
    assert changes_ids == expected


def test_repr(sample):
    assert repr(sample.changes) == "<TrackedChanges tag=text:tracked-changes>"


def test_str(sample):
    result = str(sample.changes)
    assert "Romain" in result
    assert "2009-08-21" in result
