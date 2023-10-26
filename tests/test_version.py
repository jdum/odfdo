# Copyright 2018-2023 Jérôme Dumonteil
# Authors (odfdo project): jerome.dumonteil@gmail.com

from pathlib import Path

from odfdo.version import __version__


def test_version():
    assert __version__
    assert isinstance(__version__, str)
