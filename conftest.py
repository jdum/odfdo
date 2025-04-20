"""Configuration and injectable fixtures for Pytest."""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    os.environ["ODFDO_TESTING"] = "1"
    os.environ["ODFDO_TESTING_PERFS"] = "1"


@pytest.fixture(scope="session")
def samples():
    folder = Path(__file__).parent / "tests" / "samples"

    def sample_path(filename: str) -> Path:
        return folder / filename

    return sample_path


@pytest.fixture(scope="session")
def samples_dir():
    return Path(__file__).parent / "tests" / "samples"


def pytest_unconfigure(config):
    for key in ("ODFDO_TESTING", "ODFDO_TESTING_PERFS"):
        try:
            os.environ.pop(key)
        except KeyError:
            print(f"{key} not in environment")
