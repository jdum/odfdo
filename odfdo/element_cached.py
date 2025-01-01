# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""CachedElement base class of Table and Row, and caching functions.
"""
from __future__ import annotations

from bisect import bisect_left, insort

from lxml.etree import XPath, _Element

from .element import Element, xpath_compile


class CachedElement(Element):

    def _copy_cache(self, cache: tuple | None) -> None:
        """Copy cache when cloning."""
        if cache:
            self._tmap = cache[0]
            self._cmap = cache[1]
            if len(cache) == 3:
                self._rmap = cache[2]

    def get_elements(self, xpath_query: XPath | str) -> list[Element]:
        cache: tuple | None = None
        element = self._Element__element
        if isinstance(xpath_query, str):
            new_xpath_query = xpath_compile(xpath_query)
            result = new_xpath_query(element)
        else:
            result = xpath_query(element)
        if not isinstance(result, list):
            raise TypeError("Bad XPath result")

        if hasattr(self, "_rmap"):
            cache = (self._tmap, self._cmap, self._rmap)
        else:
            cache = (self._tmap, self._cmap)
        return [
            Element.from_tag_for_clone(e, cache)
            for e in result
            if isinstance(e, _Element)
        ]

    def clear(self) -> None:
        """Remove text, children and attributes from the element."""
        self._Element__element.clear()
        if hasattr(self, "_tmap"):
            self._tmap: list[int] = []
        if hasattr(self, "_cmap"):
            self._cmap: list[int] = []
        if hasattr(self, "_rmap"):
            self._rmap: list[int] = []
        if hasattr(self, "_indexes"):
            remember = False
            if "_rmap" in self._indexes:
                remember = True
            self._indexes: dict[str, dict] = {}
            self._indexes["_cmap"] = {}
            self._indexes["_tmap"] = {}
            if remember:
                self._indexes["_rmap"] = {}


def set_item_in_vault(  # noqa: C901
    position: int,
    item: CachedElement,
    vault: CachedElement,
    vault_scheme: XPath,
    vault_map_name: str,
    clone: bool = True,
) -> CachedElement:
    """Set the item (cell, row) in its vault (row, table), updating the
    cache map.
    """
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    repeated = item.repeated or 1  # type: ignore
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before - repeated
    if repeated_before >= 1:
        # Update repetition
        current_item._set_repeated(repeated_before)
        target_idx += 1
    else:
        # Replacing the first occurence
        vault.delete(current_item)
    # Insert new element
    if clone:
        new_item = item.clone
    else:
        new_item = item
    vault.insert(new_item, position=target_idx)
    # Insert the remaining repetitions
    if repeated_after >= 1:
        after_item = current_item.clone
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position=target_idx + 1)
    # setting a repeated item !
    if repeated_after < 0:
        # deleting some overlapped items
        deleting = repeated_after
        while deleting < 0:
            delete_item = vault._get_element_idx2(vault_scheme, target_idx + 1)
            if delete_item is None:
                break
            is_repeated = delete_item.repeated or 1  # type: ignore
            is_repeated += deleting
            if is_repeated > 1:
                delete_item._set_repeated(is_repeated)  # type: ignore
            else:
                vault.delete(delete_item)
            deleting = is_repeated
    # update cache
    # remove existing
    idx = odf_idx
    emap = _erase_map_once(vault_map, idx)
    # add before if any:
    if repeated_before >= 1:
        emap = insert_map_once(emap, idx, repeated_before)
        idx += 1
    # add our slot
    emap = insert_map_once(emap, idx, repeated)
    # add after if any::
    if repeated_after >= 1:
        idx += 1
        emap = insert_map_once(emap, idx, repeated_after)
    if repeated_after < 0:
        idx += 1
        while repeated_after < 0:
            if idx < len(emap):
                emap = _erase_map_once(emap, idx)
            repeated_after += 1
    setattr(vault, vault_map_name, emap)
    return new_item


def insert_item_in_vault(
    position: int,
    item: CachedElement,
    vault: CachedElement,
    vault_scheme: XPath,
    vault_map_name: str,
) -> CachedElement:
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    repeated = item.repeated or 1  # type: ignore
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before
    new_item = item.clone
    if repeated_before >= 1:
        current_item._set_repeated(repeated_before)
        vault.insert(new_item, position=target_idx + 1)
        after_item = current_item.clone
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position=target_idx + 2)
    else:
        # only insert new cell
        vault.insert(new_item, position=target_idx)
    # update cache
    if repeated_before >= 1:
        emap = _erase_map_once(vault_map, odf_idx)
        emap = insert_map_once(emap, odf_idx, repeated_before)
        emap = insert_map_once(emap, odf_idx + 1, repeated)
        setattr(
            vault, vault_map_name, insert_map_once(emap, odf_idx + 2, repeated_after)
        )
    else:
        setattr(vault, vault_map_name, insert_map_once(vault_map, odf_idx, repeated))
    return new_item


def delete_item_in_vault(
    position: int,
    vault: CachedElement,
    vault_scheme: XPath,
    vault_map_name: str,
) -> None:
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    # current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    new_repeated = current_repeated - 1
    if new_repeated >= 1:
        current_item._set_repeated(new_repeated)
        setattr(
            vault,
            vault_map_name,
            vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx:]],
        )
    else:
        # actual erase
        vault.delete(current_item)
        setattr(
            vault,
            vault_map_name,
            vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx + 1 :]],
        )


def insert_map_once(orig_map: list, odf_idx: int, repeated: int) -> list[int]:
    """Add an item (cell or row) to the map

        map  --  cache map

        odf_idx  --  index in ODF XML

        repeated  --  repeated value of item, 1 or more

    odf_idx is NOT position (col or row), neither raw XML position, but ODF index
    """
    repeated = repeated or 1
    if odf_idx > len(orig_map):
        raise IndexError
    if odf_idx > 0:
        before = orig_map[odf_idx - 1]
    else:
        before = -1
    juska = before + repeated  # aka max position value for item
    if odf_idx == len(orig_map):
        insort(orig_map, juska)
        return orig_map
    new_map = orig_map[:odf_idx]
    new_map.append(juska)
    new_map.extend([(x + repeated) for x in orig_map[odf_idx:]])
    return new_map


def _erase_map_once(orig_map: list, odf_idx: int) -> list[int]:
    """Remove an item (cell or row) from the map

    map  --  cache map

    odf_idx  --  index in ODF XML
    """
    if odf_idx >= len(orig_map):
        raise IndexError
    if odf_idx > 0:
        before = orig_map[odf_idx - 1]
    else:
        before = -1
    current = orig_map[odf_idx]
    repeated = current - before
    orig_map = orig_map[:odf_idx] + [(x - repeated) for x in orig_map[odf_idx + 1 :]]
    return orig_map


def make_cache_map(idx_repeated_seq: list[tuple[int, int]]) -> list[int]:
    """Build the initial cache map of the table."""
    cache_amp: list[int] = []
    for odf_idx, repeated in idx_repeated_seq:
        cache_amp = insert_map_once(cache_amp, odf_idx, repeated)
    return cache_amp


def find_odf_idx(cache_map: list, position: int) -> int | None:
    """Find odf_idx in the map from the position (col or row)."""
    odf_idx = bisect_left(cache_map, position)
    if odf_idx < len(cache_map):
        return odf_idx
    return None
