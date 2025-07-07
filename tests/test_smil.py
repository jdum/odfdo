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


from odfdo.smil import AnimPar, AnimSeq, AnimTransFilter


def test_anim_par_class():
    ap = AnimPar()
    assert isinstance(ap, AnimPar)


def test_anim_seq_class():
    seq = AnimSeq()
    assert isinstance(seq, AnimSeq)


def test_anim_tf_class():
    atf = AnimTransFilter()
    assert isinstance(atf, AnimTransFilter)


def test_anim_par_node():
    ap = AnimPar(presentation_node_type="timing-root")
    assert ap.presentation_node_type == "timing-root"


def test_anim_par_smil_begin():
    ap = AnimPar(smil_begin="10s")
    assert ap.smil_begin == "10s"


def test_anim_seq_node():
    seq = AnimSeq(presentation_node_type="timing-root")
    assert seq.presentation_node_type == "timing-root"


def test_anim_tf_args():
    atf = AnimTransFilter(
        smil_dur="2s",
        smil_type="barWipe",
        smil_subtype="leftToRight",
        smil_direction="forward",
        smil_fadeColor="#000000",
        smil_mode="in",
    )
    assert atf.smil_dur == "2s"
    assert atf.smil_type == "barWipe"
    assert atf.smil_subtype == "leftToRight"
    assert atf.smil_direction == "forward"
    assert atf.smil_fadeColor == "#000000"
    assert atf.smil_mode == "in"
