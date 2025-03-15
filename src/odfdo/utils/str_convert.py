# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
from __future__ import annotations

from typing import Any


def to_bytes(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def to_str(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def str_to_bytes(text: str) -> bytes:
    return text.encode("utf-8", "replace")


def bytes_to_str(text: bytes) -> str:
    return text.decode("utf-8", "ignore")
