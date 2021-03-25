#!/bin/bash
#
# if pdoc is missing: pip install pdoc3
#

[ -d doc.old ] && rm -r doc.old
[ -d doc ] && mv doc doc.old
pdoc -f --html odfdo
mv html/odfdo doc
mv html doc.old
cp odfdo.png doc
