#!/bin/bash

[ -f gen_doc.sh ] || {
    echo "Not in top directory" ; exit 1
}

[ -d doc ] && rm -fr doc

cp -f odfdo.png doc_src/src
cp -f README.md doc_src/src
cp -f CHANGES.md doc_src/src
cd doc_src
rm -fr site
python << END
import os
from importlib import import_module
from pathlib import Path

file = Path('src/recipes.md').open('w', encoding='utf8')
file.write("# Recipes\n\n")
file.write("Recipes source code is in the \`/recipes\` directory of \`odfdo\` sources.\n")
file.write("Most recipes are autonomous scripts doing actual modifications of ODF sample files, you can check the results in the \`recipes/recipes_output\` directory.\n\n")
os.chdir('../recipes')
mods = {}
for path in Path('.').glob('*.py'):
    mod = import_module(str(path.stem))
    seq = getattr(mod, "_DOC_SEQUENCE", 1000 + len(mods))
    while seq in mods:
        seq += 1
    mods[seq] = (mod, path)
for key in sorted(mods.keys()):
    print('recipe:', path.stem)
    mod, path = mods[key]
    file.write(f'### {path.stem.replace("_", " ").capitalize()}\n\n')
    file.write(f'{mod.__doc__}\n\n')
    file.write(f'??? code "recipes/{path.name}"\n')
    file.write("    \`\`\`python\n")
    file.write(f'    {{% include "../../recipes/{path.name}" %}}\n')
    file.write("    \`\`\`\n\n")
file.close()
END
mkdocs build
mv site ../doc
rm -fr site
