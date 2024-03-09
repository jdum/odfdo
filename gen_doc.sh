#!/bin/bash
pip install -U pdoc

[ -d doc ] && rm -fr doc
mkdir doc
cp odfdo.png doc
pdoc -o doc --search --logo "https://raw.githubusercontent.com/jdum/odfdo/master/odfdo.png" --logo-link "https://github.com/jdum/odfdo" ./odfdo
