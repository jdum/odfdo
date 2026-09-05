# Copyright 2018-2026 Jérôme Dumonteil
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
"""JSON formater for pretty export."""

from __future__ import annotations

import json
from typing import Any


def format_json(
    obj: Any,
    indent: int = 2,
    ensure_ascii: bool = False,
    _level: int = 0,
) -> str:
    """Format a dictionary or matrix of values into a pretty JSON string.

    Keep 1D row lists of primitives on a single line.

    Args:
        obj: The object to format (dict, list, or primitive).
        indent: Indentation level for formatting.
        ensure_ascii: If True, non-ASCII characters are escaped.
        _level: Current indentation level for recursion.

    Returns:
        str: The formatted JSON string.
    """
    spacing = " " * (indent * _level)
    child_spacing = " " * (indent * (_level + 1))

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            k_str = json.dumps(k, ensure_ascii=ensure_ascii)
            v_str = format_json(
                v,
                indent=indent,
                ensure_ascii=ensure_ascii,
                _level=_level + 1,
            )
            items.append(f"{child_spacing}{k_str}: {v_str}")
        return "{\n" + ",\n".join(items) + f"\n{spacing}}}"

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if not any(isinstance(x, (dict | list)) for x in obj):
            return json.dumps(obj, ensure_ascii=ensure_ascii)
        items = [
            f"{child_spacing}{format_json(x, indent=indent, ensure_ascii=ensure_ascii, _level=_level + 1)}"
            for x in obj
        ]
        return "[\n" + ",\n".join(items) + f"\n{spacing}]"

    return json.dumps(obj, ensure_ascii=ensure_ascii)
