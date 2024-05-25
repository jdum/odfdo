#!/bin/bash

[ -f gen_doc.sh ] || {
    echo "Not in top directory" ; exit 1
}

pip install -U mkdocs mkdocs-material mkdocstrings[python]

[ -d doc ] && rm -fr doc

cp -f odfdo.png doc_src/src
cp -f README.md doc_src/src
cp -f CHANGES.md doc_src/src
cd doc_src
rm -fr site
mkdocs build
mv site ../doc
rm -fr site
