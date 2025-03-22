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

from collections.abc import Iterable
from textwrap import dedent

import pytest

from odfdo.document import Document
from odfdo.paragraph import Paragraph


@pytest.fixture
def document_base(samples) -> Iterable[Document]:
    document = Document(samples("base_text.odt"))
    yield document


@pytest.fixture
def document_example(samples) -> Iterable[Document]:
    document = Document(samples("example.odt"))
    yield document


@pytest.fixture
def document_bookmark(samples) -> Iterable[Document]:
    document = Document(samples("bookmark.odt"))
    yield document


@pytest.fixture
def document_i28(samples) -> Iterable[Document]:
    document = Document(samples("issue_28_pretty.odt"))
    yield document


@pytest.fixture
def document_list(samples) -> Iterable[Document]:
    document = Document(samples("list.odt"))
    yield document


@pytest.fixture
def document_meta(samples) -> Iterable[Document]:
    document = Document(samples("meta.odt"))
    yield document


@pytest.fixture
def document_note(samples) -> Iterable[Document]:
    document = Document(samples("note.odt"))
    yield document


@pytest.fixture
def document_pb(samples) -> Iterable[Document]:
    document = Document(samples("pagebreak.odt"))
    yield document


@pytest.fixture
def document_toc2(samples) -> Iterable[Document]:
    document = Document(samples("toc_done.odt"))
    yield document


@pytest.fixture
def document_toc(samples) -> Iterable[Document]:
    document = Document(samples("toc.odt"))
    yield document


@pytest.fixture
def document_tc(samples) -> Iterable[Document]:
    document = Document(samples("tracked_changes.odt"))
    yield document


@pytest.fixture
def document_uf(samples) -> Iterable[Document]:
    document = Document(samples("user_fields.odt"))
    yield document


@pytest.fixture
def document_var(samples) -> Iterable[Document]:
    document = Document(samples("variable.odt"))
    yield document


@pytest.fixture
def document_case1(samples) -> Iterable[Document]:
    document = Document(samples("base_md_text.odt"))
    yield document


@pytest.fixture
def document_case2(samples) -> Iterable[Document]:
    document = Document(samples("md_style.odt"))
    yield document


@pytest.fixture
def document_case3(samples) -> Iterable[Document]:
    document = Document(samples("md_fixed.odt"))
    yield document


@pytest.fixture
def document_dormeur(samples) -> Iterable[Document]:
    document = Document(samples("dormeur_notes.odt"))
    yield document


@pytest.fixture
def document_lorem(samples) -> Iterable[Document]:
    document = Document(samples("lorem.odt"))
    yield document


@pytest.fixture
def document_img(samples) -> Iterable[Document]:
    document = Document(samples("chair.odt"))
    yield document


@pytest.fixture
def document_tab(samples) -> Iterable[Document]:
    document = Document(samples("table.odt"))
    yield document


def test_md_doc_ods():
    doc = Document("ods")
    with pytest.raises(NotImplementedError):
        _md = doc.to_markdown()


def test_md_doc_drawing():
    doc = Document("drawing")
    with pytest.raises(NotImplementedError):
        _md = doc.to_markdown()


def test_md_doc_empty():
    doc = Document("odt")
    md = doc.to_markdown()
    assert md == ""


def test_md_doc_minimal():
    text = "some text"
    doc = Document("odt")
    doc.body.clear()
    doc.body.append(Paragraph(text))
    md = doc.to_markdown()
    assert md.strip() == text


def test_md_base_text(document_base):
    md = document_base.to_markdown()
    expected = dedent(
        """\
    # odfdo Test Case Document

    This is the first paragraph.

    This is the second paragraph.

    This is a paragraph with a named style.

    ## Level 2 Title

    This is the first paragraph of the second title.

    This is the last paragraph with diacritical signs: éè

    # First Title of the Second Section

    First paragraph of the second section.

    This is the second paragraph with [an external link](https://github.com/jdum/odfdo) inside.
    """
    ).strip()
    assert md.strip() == expected


def test_md_example_text(document_example):
    md = document_example.to_markdown()
    expected = dedent(
        """\
    # odfdo Test Case Document

    This is the first paragraph.

    This is the second paragraph.

    This is a paragraph with a named style.

    ## Level 2 Title

    This is the first paragraph of the second title.

    This is the last paragraph with diacritical signs: éè

    # First Title of the Second Section

    First paragraph of the second section.
    """
    ).strip()
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_bookmark_text(document_bookmark):
    md = document_bookmark.to_markdown()
    expected = "Lettre à Élise (cf. page 1)."
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_i28_text(document_i28):
    md = document_i28.to_markdown()
    expected = (
        "This is an example with => v8.1.4 <= spaces after "
        "reading and writing with odfdo."
    )
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_list_text(document_list):
    md = document_list.to_markdown()
    expected = dedent(
        """\
        Some text

         -  une liste accentuée
            -  un sous\\-élément

         1. une liste numérotée
         2. et de deux !
    """
    ).strip()
    # First paragraphAuteur inconnu2009-06-22T17:18:42This is an annotation.With diacritical signs: éè
    assert md.strip() == expected


def test_md_meta_text(document_meta):
    md = document_meta.to_markdown()
    expected = "Only testing meta.xml here…"
    assert md.strip() == expected


def test_md_note_text(document_note):
    md = document_note.to_markdown()
    expected = dedent(
        """\
    Un paragraphe[1] d'apparence[i] banale.

    1. C'est-à-dire l'élément « text:p ».

    i. Les apparences sont trompeuses !
    """  # noqa: RUF001
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_pagebreak_text(document_pb):
    md = document_pb.to_markdown()
    expected = dedent(
        """\
    first paragraph

    second paragraph
    """
    ).strip()
    assert md.strip() == expected


def test_md_toc_text(document_toc):
    md = document_toc.to_markdown()
    expected = dedent(
        """\
    # Level 1 title 1

    ## Level 2 title 1

    # Level 1 title 2

    ### Level 3 title 1

    ## Level 2 title 2

    # Level 1 title 3

    ## Level 2 title 1

    ### Level 3 title 1

    ### Level 3 title 2

    ## Level 2 title 2

    ### Level 3 title 1

    ### Level 3 title 2

    """
    ).strip()
    assert md.strip() == expected


def test_user_fields_text(document_uf):
    md = document_uf.to_markdown()
    expected = dedent(
        """\
    A document with user\\-field declarations.

    Paris

    77 77 77 77 77

    42
    """
    ).strip()
    assert md.strip() == expected


def test_md_variable_text(document_var):  # FAIL
    md = document_var.to_markdown()
    expected = dedent(
        """\
    Today is 12/08/09 15:17:27.

    This document is named Intitulé.

    This is page 1 out of 1.

    Reference to page 1.

    Declaring variable 123.

    Inserting variable 123.

    Inserting a user field VRAI.
    """
    ).strip()
    assert md.strip() == expected


def test_md_case1_text(document_case1):  # FAIL
    md = document_case1.to_markdown()
    expected = dedent(
        """\
        # odfdo Test Case Document

        This is the first paragraph with a link: [the odfdo project](https://github.com/jdum/odfdo).

        This is the second paragraph.

        This is a paragraph with a named style.

        Some list :

         -  item1
         -  item2
         -  item3
            -  sub item a
            -  sub item (with link: [odfdo b link](https://github.com/jdum/odfdo)) b
            -  sub item c
         -  item4

        last paragraph

        ## Level 2 Title with [odfdo project again](https://github.com/jdum/odfdo) embeded

        This is the first paragraph of the second title.

        This is the last paragraph with diacritical signs: éè

        # First Title of the Second Section

        First paragraph of the second section.
    """
    ).strip()
    print(md.strip())
    assert md.strip() == expected


def test_md_case2_text(document_case2):  # FAIL
    # Here  **bolded space** at *begin*.
    # Some style here and *there*

    md = document_case2.to_markdown()
    expected = dedent(
        """\
        # odfdo Test Case2

        Some style `here` and _there_

        Two spaces at start

        ~~somme modified~~

        =7 Starting spaces This is the second paragraph.

        One tab

        Two tabs

        This is a **bold** **paragraph** with a named style.

        Here  **bolded space** at _begin_.

        Some _special_ ***case*** _to_ check if ~~barred~~

        Some list :

         -  item1
         -  **item2**
         -  `item3`
         -  ***item4***
         -  item5

            1. a
            2. b

               -  aaa
               -  eee
                  -  ~~zzzz~~
                  -  zzzz
               -  iii

            3. c

         -  _item6_
         -  [x] done

            1. u
            2. v
            3. w

         -  [ ] undone
         -

        last paragraph _with italic_

        \\#\\#\\#\\# To see **\\*\\*stars\\*\\*** or \\*\\*any\\*\\*

        and **\\*more\\*** and \\~\\~maybe\\~\\~

        ## Level 2 Title with [odfdo project again](https://github.com/jdum/odfdo) embeded

        This is the first paragraph of the second title.

         1. One
         2. **two**
            1. aa
            2. **bb**

               -  eee
               -  fff

            3. **cc**
         3. three
            1. x
            2. y
               1. p
               2. q
               3. r
            3. z
         4. four

        after
        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_case3_text(document_case3):  # FAIL
    md = document_case3.to_markdown()
    expected = dedent(
        """\
        # odfdo Test Case3

        ```
        Some text
        ```

        neutral

        ```
        several lines
        of text
        with a
        fixed style
        ```

        standard

         1. a
         2. `here `
         3. `some fixed too`
         4. hop

        ```
        another one,
        with *thing* and other things
        in it
         tabs	in same place
              spaces
        bold  or italic ?
        ```

        End here

        ```


        ```
        """  # noqa: RUF001
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_dormeur_text(document_dormeur):  # FAIL
    md = document_dormeur.to_markdown()
    expected = dedent(
        """\
        # ~~Le~~ dormeur[1] du _val_

        C'est un trou de verdure où chante une rivière,\\
        Accrochant follement aux herbes des haillons\\
        D'argent ; où le soleil, de la _montagne_[2] **fière**,\\
        Luit : c'est un petit val qui mousse de rayons.\\
        \\
        Un soldat jeune, bouche ouverte, tête nue,\\
        Et la nuque baignant dans le frais cresson bleu,\\
        Dort ; il est étendu dans l'herbe, sous la nue,\\
        Pâle dans son lit vert où la lumière pleut.\\
        \\
        Les pieds dans les glaïeuls, il dort. Souriant[i] comme\\
        Sourirait un enfant malade, il fait un somme :\\
        Nature, berce\\-le chaudement : il a froid.\\
        \\
        Les parfums ne font pas frissonner sa narine ;\\
        Il dort dans le soleil, la main sur sa poitrine,\\
        Tranquille. Il a deux trous rouges au côté droit.

        Arthur Rimbaud

        1. Note dormeur
        2. Note next [remote link](https://test.example.com/)

        i. End note

        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_lorem_text(document_lorem):  # FAIL
    md = document_lorem.to_markdown()
    expected = dedent(
        """\
        # Lorem ipsum dolor sit amet

        _Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in,_ **pretium** _a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;_ **Aliquam nibh. Mauris ac mauris sed pede pellentesque** _fermentum._

         -  Maecenas adipiscing ante non diam sodales
         -  Ut velit mauris, egestas sed, gravida nec, ornare ut, mi.

        Aenean utorci vel massa suscipit **pulvinar**.

        **Maecenas adipiscing ante non diam sodales hendrerit. Ut velit mauris, egestas sed, gravida nec, ornare ut, mi. Aenean ut orci vel massa suscipit pulvinar. Nulla sollicitudin. Fusce varius, ligula non tempus aliquam, nunc turpis ullamcorper nibh, in tempus sapien eros vitae ligula. Pellentesque rhoncus nunc et augue. Integer id felis. Curabitur aliquet pellentesque diam. Integer quis metus vitae elit lobortis egestas. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi vel erat non mauris convallis vehicula. Nulla et sapien. Integer tortor tellus, aliquam faucibus, convallis id, congue eu, quam. Mauris ullamcorper felis vitae erat. Proin feugiat, augue non elementum posuere, metus purus iaculis lectus, et tristique ligula justo vitae magna. Aliquam convallis sollicitudin purus. Praesent aliquam, enim at fermentum mollis, ligula massa adipiscing nisl, ac euismod nibh nisl eu lectus. Fusce vulputate sem at sapien. Vivamus leo. Aliquam euismod libero eu enim. Nulla nec felis sed leo placerat imperdiet. Aenean suscipit nulla in justo. Suspendisse cursus rutrum augue. Nulla tincidunt tincidunt mi. Curabitur iaculis, lorem vel rhoncus faucibus, felis magna fermentum augue, et ultricies lacus lorem varius purus.** _Curabitur_ **eu amet.**
        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_tracked_text(document_tc):  # FAIL
    md = document_tc.to_markdown()
    expected = dedent(
        """\
        Bonjour  los bonitos amigos  ça va ?
        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_toc2_text(document_toc2):
    md = document_toc2.to_markdown()
    expected = dedent(
        """\
        **Table of Contents**

        [Level 1 title 1	1](#)

        [Level 2 title 1	1](#)

        [Level 1 title 2	1](#)

        [Level 3 title 1	1](#)

        [Level 2 title 2	1](#)

        [Level 1 title 3	1](#)

        [Level 2 title 1	1](#)

        [Level 3 title 1	1](#)

        [Level 3 title 2	1](#)

        [Level 2 title 2	1](#)

        [Level 3 title 1	1](#)

        [Level 3 title 2	1](#)

        #

        # Level 1 title 1

        ## Level 2 title 1

        # Level 1 title 2

        ### Level 3 title 1

        ## Level 2 title 2

        # Level 1 title 3

        ## Level 2 title 1

        ### Level 3 title 1

        ### Level 3 title 2

        ## Level 2 title 2

        ### Level 3 title 1

        ### Level 3 title 2
    """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_img_text(document_img):  # FAIL
    md = document_img.to_markdown()
    expected = dedent(
        """\
        **Image test**

        A chair :

        ![alternate name, chair](Pictures/1000000000000094000001004C83F003.jpg)
        _Figure_ 1  _chair_
        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected


def test_md_table_text(document_tab):  # FAIL
    md = document_tab.to_markdown()
    expected = dedent(
        """\
        # First table

        | a                 | b                               | c   | d               |
        |-------------------|---------------------------------|-----|-----------------|
        | Some bar \\| there | Log or _short_ or **very** long |     | \\*\\*no\\*\\* bold |
        | 1                 | 2                               | 3   | 4               |
        | `fixed`           | 20                              | 30  | 40              |
        | 100               | **200**                         | 300 | 400             |


        # Second table

        | AAAAAAAAAAAAAAAAAA | BBBB                   | **CCC**   |                        | EE    |
        |--------------------|------------------------|-----------|------------------------|-------|
        | 1.234              | a                      | _bb_      | 2024\\-12\\-25           | \\-2   |
        | **Some title**     | Some line break inside | anchor[1] | A list of 3 paras here | `123` |


        1. Note in a cell
        """
    ).strip()
    print(repr(md.strip()))
    assert md.strip() == expected
