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

from collections import namedtuple
from collections.abc import Iterable
from datetime import datetime

import pytest

from odfdo.document import Document
from odfdo.header import Header
from odfdo.paragraph import Paragraph
from odfdo.tracked_changes import (
    ChangeInfo,
    TextChange,
    TextChangedRegion,
    TextChangeEnd,
    TextChangeStart,
    TextDeletion,
    TextFormatChange,
    TextInsertion,
    TrackedChanges,
)

Sample = namedtuple("Sample", ["doc", "changes"])


@pytest.fixture
def sample(samples) -> Iterable[Sample]:
    document = Document(samples("tracked_changes.odt"))
    yield Sample(doc=document, changes=document.body.get_tracked_changes())


@pytest.fixture
def sample_doc() -> Iterable[Document]:
    doc = Document("odt")
    body = doc.body
    body.append(Header(1, "Title"))
    body.append(Paragraph("Some text."))
    yield doc


def test_change_info_class():
    ci = ChangeInfo()
    assert isinstance(ci, ChangeInfo)


def test_change_info_class_creator():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    ci = ChangeInfo(name, dt)
    assert ci.creator == name


def test_change_info_class_date():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    ci = ChangeInfo(name, dt)
    assert ci.date == dt


def test_change_info_comments_none():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    ci = ChangeInfo(name, dt)
    assert ci.get_comments() == ""


def test_change_info_comments():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment = "Some comment"
    ci = ChangeInfo(name, dt)
    ci.set_comments(comment)
    assert ci.get_comments() == comment


def test_change_info_comments_replace():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment1 = "Some comment"
    comment2 = "More comment"
    ci = ChangeInfo(name, dt)
    ci.set_comments(comment1)
    ci.set_comments(comment2)
    assert ci.get_comments() == comment2


def test_change_info_comments_no_replace():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment1 = "Some comment"
    comment2 = "More comment"
    ci = ChangeInfo(name, dt)
    ci.set_comments(comment1)
    ci.set_comments(comment2, replace=False)
    expected = f"{comment1}\n{comment2}"
    assert ci.get_comments() == expected


def test_change_info_comments_no_replace_no_join():
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment1 = "Some comment"
    comment2 = "More comment"
    ci = ChangeInfo(name, dt)
    ci.set_comments(comment1)
    ci.set_comments(comment2, replace=False)
    expected = [comment1, comment2]
    assert ci.get_comments(joined=False) == expected


def test_text_insertion_class():
    ti = TextInsertion()
    assert isinstance(ti, TextInsertion)


def test_text_insertion_empty_deleted():
    ti = TextInsertion()
    assert ti.get_deleted() is None


def test_text_insertion_empty_deleted_as_text():
    ti = TextInsertion()
    assert ti.get_deleted(as_text=True) == ""


def test_text_insertion_empty_inserted():
    ti = TextInsertion()
    with pytest.raises(TypeError):
        ti.get_inserted()


def test_text_insertion_empty_change_info():
    ti = TextInsertion()
    assert ti.get_change_info() is None


def test_text_insertion_empty_set_change_info():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment = Paragraph("Some comment")
    ti.set_change_info(None, name, dt, comment)
    ci = ti.get_change_info()
    assert isinstance(ci, ChangeInfo)


def test_text_insertion_empty_set_change_info_comment_list():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comments = [Paragraph("Some comment"), Paragraph("Other comment")]
    ti.set_change_info(None, name, dt, comments)
    ci = ti.get_change_info()
    assert isinstance(ci, ChangeInfo)


def test_text_insertion_empty_set_change_info_get():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    comment = Paragraph("Some comment")
    ti.set_change_info(None, name, dt, comment)
    ci = ti.get_change_info()
    assert ci.creator == name
    assert ci.date == dt
    assert ci.get_comments() == str(comment).strip()


def test_text_insertion_empty_set_change_info_get_no_comment():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    ti.set_change_info(None, name, dt)
    ci = ti.get_change_info()
    assert ci.creator == name
    assert ci.date == dt
    assert ci.get_comments() == ""


def test_text_insertion_empty_set_change_info_get_comment_list():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    t1 = "Some comment"
    t2 = "Other comment"
    comments = [Paragraph(t1), Paragraph(t2)]
    ti.set_change_info(None, name, dt, comments)
    ci = ti.get_change_info()
    assert ci.creator == name
    assert ci.date == dt
    assert ci.get_comments(joined=False) == [t1, t2]


def test_text_insertion_empty_set_change_info_get_comment_list_wrong():
    ti = TextInsertion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    t1 = "Some comment"
    comments = [Paragraph(t1), "wrong"]
    with pytest.raises(TypeError):
        ti.set_change_info(None, name, dt, comments)


def test_text_insertion_get_from_text_changed_region(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    assert isinstance(cr, TextChangedRegion)
    ti = cr.get_change_element()
    assert isinstance(ti, TextInsertion)


def test_text_insertion_get_inserted(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    ti = cr.get_change_element()
    content = ti.get_inserted()
    assert isinstance(content, list)
    p = content[0]
    assert isinstance(p, Paragraph)
    assert str(p).strip() == "los bonitos amigos"


def test_text_insertion_get_inserted_as_text(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    ti = cr.get_change_element()
    content = ti.get_inserted(as_text=True)
    assert content.strip() == "los bonitos amigos"


def test_text_insertion_get_inserted_as_text_no_header(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    ti = cr.get_change_element()
    content = ti.get_inserted(as_text=True, no_header=True)
    assert content.strip() == "los bonitos amigos"


def test_text_insertion_set_ci_wrong(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    ti = cr.get_change_element()
    with pytest.raises(TypeError):
        ti.set_change_info(change_info="wrong")


def test_text_insertion_set_ci_new(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(1)
    ti = cr.get_change_element()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    ci = ChangeInfo(name, dt)
    ti.set_change_info(change_info=ci)
    new_ci = ti.get_change_info()
    assert new_ci.creator == name
    assert new_ci.date == dt


def test_text_deletion_class():
    td = TextDeletion()
    assert isinstance(td, TextDeletion)


def test_text_deletion_empty_deleted():
    td = TextDeletion()
    assert td.get_deleted() == []


def test_text_deletion_empty_deleted_as_text():
    td = TextDeletion()
    assert td.get_deleted(as_text=True) == ""


def test_text_deletion_empty_deleted_no_header():
    td = TextDeletion()
    assert td.get_deleted(no_header=True) == []


def test_text_deletion_empty_inserted():
    td = TextDeletion()
    assert td.get_inserted() is None


def test_text_deletion_empty_inserted_as_text():
    td = TextDeletion()
    assert td.get_inserted(as_text=True) == ""


def test_text_deletion_empty_change_info():
    td = TextDeletion()
    assert td.get_change_info() is None


def test_text_deletion_get_from_text_changed_region(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(0)
    assert isinstance(cr, TextChangedRegion)
    td = cr.get_change_element()
    assert isinstance(td, TextDeletion)


def test_text_deletion_get_deleted_from_text_changed_region(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(0)
    td = cr.get_change_element()
    assert len(td.get_deleted()) == 1
    assert str(td.get_deleted()[0]).strip() == "les"


def test_text_deletion_get_deleted_from_text_changed_region_as_text(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(0)
    td = cr.get_change_element()
    assert td.get_deleted(as_text=True).strip() == "les"


def test_text_deletion_get_deleted_from_text_changed_region_no_header(sample):
    tracked_changes = sample.changes
    cr = tracked_changes.get_changed_region(0)
    td = cr.get_change_element()
    assert str(td.get_deleted(no_header=True)[0]).strip() == "les"


def test_text_deletion_set_deleted(sample_doc):
    body = sample_doc.body
    p = body.get_paragraph(content="Some")
    assert isinstance(p, Paragraph)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted(p)
    assert len(td.get_deleted()) == 1


def test_text_deletion_set_deleted_list(sample_doc):
    body = sample_doc.body
    p = body.get_paragraph(content="Some")
    assert isinstance(p, Paragraph)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted([p])
    assert len(td.get_deleted()) == 1


def test_text_deletion_set_deleted_list_2(sample_doc):
    body = sample_doc.body
    h = body.get_header(content="Title")
    assert isinstance(h, Header)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted([h])
    assert len(td.get_deleted()) == 1


def test_text_deletion_set_deleted_list_3(sample_doc):
    body = sample_doc.body
    h = body.get_header(content="Title")
    assert isinstance(h, Header)
    p = body.get_paragraph(content="Some")
    assert isinstance(p, Paragraph)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted([h, p])
    assert len(td.get_deleted()) == 2


def test_text_deletion_set_deleted_list_2_replace(sample_doc):
    body = sample_doc.body
    h = body.get_header(content="Title")
    assert isinstance(h, Header)
    p = body.get_paragraph(content="Some")
    assert isinstance(p, Paragraph)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted([h])
    assert len(td.get_deleted()) == 1
    td.set_deleted([p])
    assert len(td.get_deleted()) == 1


def test_text_deletion_set_deleted_get_no_header(sample_doc):
    body = sample_doc.body
    h = body.get_header(content="Title")
    assert isinstance(h, Header)
    p = body.get_paragraph(content="Some")
    assert isinstance(p, Paragraph)
    td = TextDeletion()
    assert len(td.get_deleted()) == 0
    td.set_deleted([h, p])
    result = td.get_deleted(no_header=True)
    assert len(result) == 2
    assert isinstance(result[0], Paragraph)
    assert isinstance(result[1], Paragraph)


def test_text_format_change_class():
    tfc = TextFormatChange()
    assert isinstance(tfc, TextFormatChange)


def test_text_changed_region_class():
    tcr = TextChangedRegion()
    assert isinstance(tcr, TextChangedRegion)


def test_text_changed_region_get_changed_region(sample):
    trc = sample.doc.body.get_tracked_changes()
    assert isinstance(trc, TrackedChanges)
    tcr = trc.get_changed_region(0)
    assert isinstance(tcr, TextChangedRegion)


def test_text_changed_region_get_change_info(sample):
    trc = sample.doc.body.get_tracked_changes()
    tcr = trc.get_changed_region(0)
    ci = tcr.get_change_info()
    assert isinstance(ci, ChangeInfo)


def test_text_changed_region_set_change_info(sample):
    trc = sample.doc.body.get_tracked_changes()
    tcr = trc.get_changed_region(0)
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    new_ci = ChangeInfo(name, dt)
    tcr.set_change_info(new_ci)
    result_ci = tcr.get_change_info()
    assert result_ci.creator == name


def test_text_changed_region_set_change_info_wrong(sample):
    tcr = TextChangedRegion()
    name = "John Doe"
    dt = datetime(1977, 12, 25, 12, 0, 0)
    new_ci = ChangeInfo(name, dt)
    with pytest.raises(ValueError):
        tcr.set_change_info(new_ci)


def test_text_changed_region_set_id(sample):
    trc = sample.doc.body.get_tracked_changes()
    tcr = trc.get_changed_region(0)
    tcr.set_id("123")
    assert tcr.get_id() == "123"


def test_text_changed_region_get_xml_id(sample):
    trc = sample.doc.body.get_tracked_changes()
    tcr = trc.get_changed_region(0)
    assert tcr._get_xml_id() == "ct140266191788864"


def test_tracked_changes_class():
    tcs = TrackedChanges()
    assert isinstance(tcs, TrackedChanges)


def test_tracked_changes_per_role_deletion(sample):
    trc = sample.doc.body.get_tracked_changes()
    regions = trc.get_changed_regions(role="deletion")
    assert len(regions) == 2


def test_tracked_changes_per_role_insertion(sample):
    trc = sample.doc.body.get_tracked_changes()
    regions = trc.get_changed_regions(role="insertion")
    assert len(regions) == 1


def test_tracked_changes_per_role_insertion_empty(sample):
    trc = TrackedChanges()
    regions = trc.get_changed_regions(role="insertion")
    assert len(regions) == 0


def test_text_change_class():
    tc = TextChange()
    assert isinstance(tc, TextChange)


def test_text_change_class_base_class_1():
    tc = TextChange()
    assert tc.get_inserted() is None


def test_text_change_class_base_class_2():
    tc = TextChange()
    assert tc.get_start() is None


def test_text_change_class_base_class_3():
    tc = TextChange()
    assert tc.get_end() is None


def test_text_change_class_base_class_4():
    tc = TextChange()
    with pytest.raises(ValueError):
        tc.get_changed_region()


def test_text_change_get(sample):
    body = sample.doc.body
    changes = body.get_text_changes()
    assert len(changes) == 3


def test_text_change_get_id(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    assert change.get_id() == "ct140266191788864"


def test_text_change_set_id(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    change.set_id("aaa123")
    assert change.get_id() == "aaa123"


def test_text_get_changed_region(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    changed_region = change.get_changed_region()
    assert isinstance(changed_region, TextChangedRegion)


def test_text_get_changed_region_2(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    tracked_changes = body.get_tracked_changes()
    changed_region = change.get_changed_region(tracked_changes)
    assert isinstance(changed_region, TextChangedRegion)


def test_text_get_change_info(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    ci = change.get_change_info()
    assert isinstance(ci, ChangeInfo)
    assert ci.creator == "Romain Gauthier"


def test_text_get_change_info_2(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    tracked_changes = body.get_tracked_changes()
    ci = change.get_change_info(tracked_changes)
    assert isinstance(ci, ChangeInfo)
    assert ci.creator == "Romain Gauthier"


def test_text_get_change_element_1(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    # tracked_changes = body.get_tracked_changes()
    ce = change.get_change_element()
    assert isinstance(ce, TextDeletion)


def test_text_get_change_element_2(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    tracked_changes = body.get_tracked_changes()
    ce = change.get_change_element(tracked_changes)
    assert isinstance(ce, TextDeletion)


def test_text_get_change_element_3(sample):
    body = sample.doc.body
    change = body.get_text_changes()[1]
    ce = change.get_change_element()
    assert isinstance(ce, TextInsertion)


def test_text_get_change_element_4(sample):
    body = sample.doc.body
    change = body.get_text_changes()[2]
    ce = change.get_change_element()
    assert isinstance(ce, TextDeletion)


def test_text_get_deleted_1(sample):
    body = sample.doc.body
    change = body.get_text_changes()[0]
    ce = change.get_change_element()
    deleted = ce.get_deleted()
    assert str(deleted[0]).strip() == "les"


def test_text_get_deleted_2(sample):
    body = sample.doc.body
    change = body.get_text_changes()[1]
    ce = change.get_change_element()
    deleted = ce.get_deleted()
    assert deleted is None


def test_text_get_deleted_3(sample):
    body = sample.doc.body
    change = body.get_text_changes()[2]
    ce = change.get_change_element()
    deleted = ce.get_deleted()
    assert str(deleted[0]).strip() == "amis,"


def test_text_change_end_class():
    tce = TextChangeEnd()
    assert isinstance(tce, TextChangeEnd)


def test_text_change_end_none_start():
    tce = TextChangeEnd()
    assert tce.get_start() is None


def test_text_change_end_get_end():
    tce = TextChangeEnd()
    assert tce.get_end() == tce


def test_text_change_end_get_deleted():
    tce = TextChangeEnd()
    assert tce.get_deleted() is None


def test_text_change_end_get_inserted_0():
    tce = TextChangeEnd()
    assert tce.get_inserted() is None


def test_text_change_end_get_inserted_1():
    tce = TextChangeEnd()
    assert tce.get_inserted(as_text=True) == ""


def test_text_change_start_class():
    tcst = TextChangeStart()
    assert isinstance(tcst, TextChangeStart)


def test_text_change_start_none_start():
    tcst = TextChangeStart()
    assert tcst.get_start() == tcst


def test_text_change_start_get_end():
    tcst = TextChangeStart()
    assert tcst.get_end() is None


def test_text_change_start_elem_1(sample):
    body = sample.doc.body
    starts = body.get_text_change_starts()
    assert len(starts) == 1
    assert isinstance(starts[0], TextChangeStart)


def test_text_change_start_elem_2(sample):
    body = sample.doc.body
    start = body.get_text_change_start(0)
    assert isinstance(start, TextChangeStart)


def test_text_change_start_elem_3(sample):
    body = sample.doc.body
    start = body.get_text_change_start(42)
    assert start is None


def test_text_change_end_elem_1(sample):
    body = sample.doc.body
    ends = body.get_text_change_ends()
    assert len(ends) == 1
    assert isinstance(ends[0], TextChangeEnd)


def test_text_change_end_elem_2(sample):
    body = sample.doc.body
    end = body.get_text_change_end(0)
    assert isinstance(end, TextChangeEnd)


def test_text_change_end_elem_3(sample):
    body = sample.doc.body
    end = body.get_text_change_end(42)
    assert end is None


def test_text_change_start_delete(sample):
    body = sample.doc.body
    start = body.get_text_change_start(0)
    start.delete()
    start2 = body.get_text_change_start(0)
    assert start2 is None
    end2 = body.get_text_change_end(0)
    assert end2 is None


def test_text_change_start_get_deleted(sample):
    body = sample.doc.body
    start = body.get_text_change(0)
    assert isinstance(start.get_deleted()[0], Paragraph)
