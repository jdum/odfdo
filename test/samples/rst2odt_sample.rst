========================
Wiki Syntax in 3 Minutes
========================

.. contents::

A title is made by underlining
==============================

Use different underlines for subtitles
--------------------------------------

To break paragraphs, just separate them with an empty line.

Another paragraph.

- a list using dash sign
- a link to a website: http://hforge.org
- a sublist:
   * a list using star sign
   * write in *italic*, in **bold** or in ``monotype``

.. figure:: image.png
  :width: 100

  Here is the caption of this image reduced to 100 pixels in width.
  You can click on http://www.itaapy.com/images/banner/;download to see it full
  size.

You can include snippets without wiki [#]_ interpretation:

::

  class Module(Folder):

    def view(self):
      print u"Hello, world!"

    `This will not be interpreted`_

For a list of all possibilities like footnotes, tables, etc. `see the
documentation`_. You can also use the toolbar.


Tables
======

You can insert simple tables with this simple syntax:

=======  =======  ======
Input 1  Input 2  Output
-------  -------  ------
A        B        A or B
=======  =======  ======
False    False    False
True     False    True
False    True     True
True     True     True
=======  =======  ======


Or a more complicated one like the following table:

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
| body row 3 | Cells may  | - Cells   |
+------------+ span rows. | - contain |
| body row 4 |            | - blocks. |
+------------+------------+-----------+


.. _`see the documentation`:
   http://docutils.sourceforge.net/docs/user/rst/quickref.html

.. [#] see the wikipedia page: http://en.wikipedia.org/wiki/Wiki
