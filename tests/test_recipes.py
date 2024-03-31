import subprocess as sp
import sys
from pathlib import Path

import pytest

RECIPES = Path(__file__).parent.parent / "recipes"


def list_recipes() -> list[Path]:
    return list(RECIPES.glob("*.py"))


@pytest.mark.parametrize("recipe", list_recipes())
def test_recipe(recipe):
    print(recipe)
    try:
        sp.run(
            [sys.executable, recipe],
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            timeout=60,
            check=True,
            text=True,
        )
    except sp.CalledProcessError as e:
        print(e.stdout)
        raise
