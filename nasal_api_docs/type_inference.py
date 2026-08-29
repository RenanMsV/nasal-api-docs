# Copyright (C) 2012 Adrian Musceac
# Copyright (C) 2019-2026 RenanMsV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Comment-based return type inference for Nasal functions.

Scans preceding comment blocks for return type hints and maps
natural-language descriptions to canonical Nasal type names.
"""

import re
from typing import List, Optional


# Canonical Nasal types returned by typeof() plus void/unknown
TYPE_SCALAR = "scalar"
TYPE_BOOL = "bool"
TYPE_NIL = "nil"
TYPE_VECTOR = "vector"
TYPE_HASH = "hash"
TYPE_FUNC = "func"
TYPE_NODE = "node"
TYPE_VOID = "void"
TYPE_UNKNOWN = "unknown"


_TYPE_KEYWORDS = {
    # Bool
    "bool": TYPE_BOOL,
    "boolean": TYPE_BOOL,
    "true": TYPE_BOOL,
    "false": TYPE_BOOL,
    # Numbers — all scalar
    "scalar": TYPE_SCALAR,
    "number": TYPE_SCALAR,
    "double": TYPE_SCALAR,
    "float": TYPE_SCALAR,
    "int": TYPE_SCALAR,
    "integer": TYPE_SCALAR,
    "degree": TYPE_SCALAR,
    "meter": TYPE_SCALAR,
    "radian": TYPE_SCALAR,
    "angle": TYPE_SCALAR,
    "elevation": TYPE_SCALAR,
    "distance": TYPE_SCALAR,
    "speed": TYPE_SCALAR,
    "altitude": TYPE_SCALAR,
    "resolution": TYPE_SCALAR,
    # Strings — mapped to scalar per Nasal typeof behaviour
    "string": TYPE_SCALAR,
    "path": TYPE_SCALAR,
    "name": TYPE_SCALAR,
    "text": TYPE_SCALAR,
    "filename": TYPE_SCALAR,
    # Node / property
    "node": TYPE_NODE,
    "prop": TYPE_NODE,
    "property": TYPE_NODE,
    "property node": TYPE_NODE,
    # Vector / array / list
    "vector": TYPE_VECTOR,
    "array": TYPE_VECTOR,
    "list": TYPE_VECTOR,
    # Hash / dict
    "hash": TYPE_HASH,
    "dictionary": TYPE_HASH,
    "object": TYPE_HASH,
    "map": TYPE_HASH,
    # Func
    "func": TYPE_FUNC,
    "function": TYPE_FUNC,
    "callback": TYPE_FUNC,
    # Nil
    "nil": TYPE_NIL,
    "none": TYPE_NIL,
}


_ARROW_SET_PATTERN = re.compile(r"\->\s*set\b", re.IGNORECASE)
_ARROW_RETURN_PATTERN = re.compile(r"\->\s*return", re.IGNORECASE)
_ARROW_MOVE_PATTERN = re.compile(r"\->\s*move\b", re.IGNORECASE)
_ARROW_DESTROY_PATTERN = re.compile(r"\->\s*(?:delete|destroy|remove)", re.IGNORECASE)
_DESTRUCTOR_PATTERN = re.compile(r"\bdestructor\b", re.IGNORECASE)


def infer_return_type(comments: List[str]) -> str:
    """Infer the return type from a list of preceding comment lines.

    Scans comments for type-hint patterns and returns the best-guess
    Nasal type name.

    Args:
        comments: List of cleaned comment strings (without leading `#`).

    Returns:
        One of: ``scalar``, ``bool``, ``nil``, ``vector``, ``hash``,
        ``func``, ``node``, ``void``, ``unknown``.
    """
    if not comments:
        return TYPE_UNKNOWN

    combined = " ".join(comments).lower()

    # 1. Check for void indicators
    if _is_void(combined):
        return TYPE_VOID

    # 2. Check for arrow patterns
    arrow_result = _check_arrow_patterns(combined)
    if arrow_result:
        return arrow_result

    # 3. Check for "returns ..." patterns
    returns_result = _check_returns_patterns(combined)
    if returns_result:
        return returns_result

    # 4. Fallback: scan for type keywords
    return _scan_for_type_keywords(combined)


def _is_void(text: str) -> bool:
    """Check if the comment indicates a void / no-return function."""
    void_indicators = [
        r"\bdestructor\b",
        r"\bclass destructor\b",
        r"\->\s*set\b",
        r"\->\s*move\b",
        r"\->\s*(?:delete|destroy|remove)\b",
        r"\bset\s+\./",
        r"\bset\b\s*(?:./|->)",
        r"\bremovelistener\b",
        r"\bremoveat\b",
    ]
    for pattern in void_indicators:
        if re.search(pattern, text):
            return True
    return False


def _check_arrow_patterns(text: str) -> Optional[str]:
    """Check arrow-based comment patterns like '-> return double'."""
    # Pattern: "-> return ... something as double"
    m = re.search(r"\->\s*return.*?(?:as\s+)?(\w+)", text)
    if m:
        keyword = m.group(1).lower()
        mapped = _TYPE_KEYWORDS.get(keyword)
        if mapped:
            return mapped

    # Pattern: "-> set" → void
    if _ARROW_SET_PATTERN.search(text):
        return TYPE_VOID
    if _ARROW_RETURN_PATTERN.search(text) and not _ARROW_SET_PATTERN.search(text):
        pass  # handled below via returns patterns

    return None


def _check_returns_patterns(text: str) -> Optional[str]:
    """Check 'returns ...' comment patterns."""
    # "returns nothing"
    if re.search(r"\breturns\s+nothing\b", text):
        return TYPE_VOID

    # "returns nil"
    if re.search(r"\breturns\s+nil\b", text):
        return TYPE_NIL

    # "returns true/false" or "returns boolean" or "returns true or false"
    if re.search(r"\breturns\s+(?:true|false|boolean|true\s+or\s+false)\b", text):
        return TYPE_BOOL

    # "returns whether" implies boolean
    if re.search(r"\breturns\s+whether\b", text):
        return TYPE_BOOL

    # "returns a bool" / "returns an bool"
    m = re.search(r"\breturns\s+(?:an?\s+)?(?:a\s+)?(?:boolean|bool)\b", text)
    if m:
        return TYPE_BOOL

    # "returns a <type>" / "returns an <type>" — capture the type word
    m = re.search(r"\breturns\s+(?:an?\s+)?(?:a\s+)?(\w+)", text)
    if m:
        keyword = m.group(1).lower()
        mapped = _TYPE_KEYWORDS.get(keyword)
        if mapped:
            return mapped

    return None


def _scan_for_type_keywords(text: str) -> str:
    """Scan comment text for known type keywords as fallback."""
    # Check for specific type keywords — use word boundaries to avoid
    # partial matches (e.g. "string" should not match "stringify")
    for keyword, nasal_type in _TYPE_KEYWORDS.items():
        # Use word boundary matching for single words
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return nasal_type

    return TYPE_UNKNOWN


def _extract_type_from_description(desc: str) -> str:
    """Extract type from a description string (e.g. 'double' from 'as double')."""
    words = desc.lower().split()
    for word in words:
        cleaned = re.sub(r'[^a-z]', '', word)
        if cleaned in _TYPE_KEYWORDS:
            return _TYPE_KEYWORDS[cleaned]
    return TYPE_UNKNOWN