"""Configuration and injectable fixtures for Pytest.
"""

import os


def pytest_configure(config):
    os.environ["ODFDO_TESTING"] = "1"


def pytest_unconfigure(config):
    try:
        os.environ.pop("ODFDO_TESTING")
    except KeyError:
        print("ODFDO_TESTING not in environment")
