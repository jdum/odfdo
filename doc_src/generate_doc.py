import ast
import os
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
MKDOCS_YML = DOC_SRC / "mkdocs.yml"

# List of modules to document (manually curated)
REFERENCE_MODULES = [
    # Core modules
    "annotation",
    "body",
    "bookmark",
    "cell",
    "column",
    "config_elements",
    "const",
    "container",
    "content",
    "datatype",
    "document",
    "draw_page",
    "element",
    "element_strip",
    "element_typed",
    "elements_between",
    "form",
    "form_controls",
    "form_controls_mixins",
    "form_properties",
    "frame",
    "header",
    "header_rows",
    "image",
    "line_break",
    "link",
    "list",
    "manifest",
    "master_page",
    "meta",
    "meta_auto_reload",
    "meta_field",
    "meta_hyperlink_behaviour",
    "meta_template",
    "meta_user_defined",
    "named_range",
    "note",
    "office_forms",
    "page_layout",
    "paragraph",
    "presentation_notes",
    "reference",
    "row",
    "row_group",
    "ruby_base",
    "section",
    "settings",
    "shapes",
    "smil",
    "spacer",
    "span",
    "style",
    "style_base",
    "style_containers",
    "style_defaults",
    "style_props",
    "style_utils",
    "styles",
    "svg",
    "tab",
    "table",
    "table_cache",
    "text_index",
    "toc",
    "tracked_changes",
    "unit",
    "user_field",
    "user_field_declaration",
    "variable",
    "variable_declaration",
    "version",
    "xmlpart",
    # Mixin modules (excluding mixin_md - internal markdown mixins)
    "mixin_dc_creator",
    "mixin_dc_date",
    "mixin_link",
    "mixin_list",
    "mixin_named_range",
    "mixin_paragraph",
    "mixin_paragraph_formatted",
    "mixin_toc",
    # Utilities
    "utils",
]


def clean_dirs() -> None:
    shutil.rmtree(DEST, ignore_errors=True)
    shutil.rmtree(SITE, ignore_errors=True)
    # Ensure src is a directory
    if SRC.exists() and not SRC.is_dir():
        SRC.unlink()
    SRC.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "odfdo.png", SRC)
    shutil.copy(ROOT / "README.md", SRC)
    shutil.copy(ROOT / "CHANGES.md", SRC)


def generate_reference_files() -> None:
    """Generate reference markdown files from module list."""
    SRC.mkdir(parents=True, exist_ok=True)
    for module in REFERENCE_MODULES:
        # Format title: "mixin_paragraph" -> "Mixin Paragraph"
        title = module.replace("_", " ").title()
        content = f"# {title}\n\n::: odfdo.{module}\n"
        (SRC / f"reference_{module}.md").write_text(content)
    print(f"Generated {len(REFERENCE_MODULES)} reference files")


def update_mkdocs_nav() -> None:
    """Update the nav section in mkdocs.yml with reference files."""
    content = MKDOCS_YML.read_text()

    # Build reference section
    ref_lines = ["    - Reference:"]
    for module in REFERENCE_MODULES:
        ref_lines.append(f"          - {module}: reference_{module}.md")

    ref_section = "\n".join(ref_lines)

    # Find and replace the Reference section in nav
    lines = content.splitlines()
    new_lines = []
    in_ref_section = False
    ref_section_done = False

    for line in lines:
        if line.strip().startswith("- Reference:") and not ref_section_done:
            new_lines.append(ref_section)
            in_ref_section = True
            ref_section_done = True
            continue

        if in_ref_section:
            # Check if we're leaving the reference section (next top-level item)
            if line.startswith("    - ") and "Reference" not in line:
                in_ref_section = False
                new_lines.append(line)
            elif line.strip() == "" or line.startswith("          - "):
                # Still in reference section, skip old entries
                continue
            else:
                in_ref_section = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    MKDOCS_YML.write_text("\n".join(new_lines))
    print(f"Updated {MKDOCS_YML}")


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
    env = dict(os.environ)
    env["NO_MKDOCS_2_WARNING"] = "1"
    result = sp.run(
        ["mkdocs", "build"],
        cwd=DOC_SRC,
        env=env,
        capture_output=True,
        text=True,
    )
    # Filter out mkdocs_autorefs warnings about ambiguous anchors
    for line in result.stdout.splitlines():
        if "WARNING" in line and "mkdocs_autorefs" in line:
            continue
        print(line)
    for line in result.stderr.splitlines():
        if "WARNING" in line and "mkdocs_autorefs" in line:
            continue
        print(line, file=__import__("sys").stderr)
    shutil.move(SITE, DEST)


def main() -> None:
    clean_dirs()
    generate_reference_files()
    update_mkdocs_nav()
    recipes = recipes_sequence()
    write_recipes_header()
    add_recipe_blocks(recipes)
    make_doc()


if __name__ == "__main__":
    main()
