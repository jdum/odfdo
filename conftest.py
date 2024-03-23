"""Configuration and injectable fixtures for Pytest.
"""

import os


def pytest_configure(config):
    os.environ["ODFDO_TESTING"] = "1"
    os.environ["ODFDO_TESTING_PERFS"] = "1"


def pytest_unconfigure(config):
    for key in ("ODFDO_TESTING", "ODFDO_TESTING_PERFS"):
        try:
            os.environ.pop(key)
        except KeyError:
            print(f"{key} not in environment")
