import ast
import shutil
import subprocess as sp
from pathlib import Path

DOC_SRC = Path(__file__).parent
ROOT = DOC_SRC.parent
SRC = DOC_SRC / "src"
RECIPES_MD = SRC / "recipes.md"
SITE = DOC_SRC / "site"
DEST = DOC_SRC / ".." / "docs"
RECIPES = ROOT / "recipes"


def clean_dirs() -> None:
    shutil.rmtree(DEST, ignore_errors=True)
    shutil.rmtree(SITE, ignore_errors=True)
    shutil.copy(ROOT / "odfdo.png", SRC)
    shutil.copy(ROOT / "README.md", SRC)
    shutil.copy(ROOT / "CHANGES.md", SRC)


def write_recipes_header() -> None:
    header = (
        "# Recipes\n\n"
        "Recipes source code is in the `/recipes` directory "
        "of `odfdo` sources.\n"
        "Most recipes are autonomous scripts doing actual modifications "
        "of ODF sample files, you can check the results in the "
        "`recipes/recipes_output` directory.\n\n"
    )
    RECIPES_MD.write_text(header)


def get_seq_docstring(path: Path) -> tuple[int, str]:
    sequence = 0
    docstring = ""
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_DOC_SEQUENCE":
                    sequence = int(ast.literal_eval(node.value))
                    break
    if (
        isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        docstring = tree.body[0].value.value
    return sequence, docstring


def recipes_sequence() -> dict[int, tuple[Path, str]]:
    recipes: dict[int, tuple[Path, str]] = {}
    for path in RECIPES.glob("*.py"):
        sequence, docstring = get_seq_docstring(path)
        if not sequence:
            sequence = 5000 + len(recipes)
        while sequence in recipes:
            sequence += 1
        recipes[sequence] = (path, docstring)
    return recipes


def add_recipe_blocks(recipes: dict[int, tuple[Path, str]]) -> None:
    with RECIPES_MD.open("a") as file:
        for key in sorted(recipes.keys()):
            path, docstring = recipes[key]
            print("recipe:", path.stem)
            file.write(f"## {path.stem.replace('_', ' ').capitalize()}\n\n")
            file.write(f"{docstring}\n\n")
            file.write(f'??? code "recipes/{path.name}"\n')
            file.write("    ```python\n")
            file.write(f'    {{% include "../../recipes/{path.name}" %}}\n')
            file.write("    ```\n\n")


def make_doc() -> None:
    sp.run(["mkdocs", "build"], cwd=DOC_SRC)  # noqa: S607
    shutil.move(SITE, DEST)


def main() -> None:
    clean_dirs()
    recipes = recipes_sequence()
    write_recipes_header()
    add_recipe_blocks(recipes)
    make_doc()


if __name__ == "__main__":
    main()
