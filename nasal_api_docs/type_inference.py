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


def infer_arg_types(comments: List[str], args: List[str]) -> List[str]:
    """Infer parameter types from comment patterns.

    Strategies (applied in order):
    1. Inline signature patterns like ``func_name(type)`` or ``func_name(type1, type2)``
    2. SYNOPSIS angle-bracket patterns like ``<type>``
    3. Description patterns like ``param_name ... type_description``
    4. Default-value hints from arg strings (``param = 0`` → scalar)

    Args:
        comments: List of cleaned comment strings.
        args: List of raw argument strings from the parser.

    Returns:
        List of type strings parallel to ``args``.  Unknown parameters
        receive an empty string.
    """
    if not comments or not args:
        return [""] * len(args)

    combined = " ".join(comments)
    arg_names = [a.split("=")[0].strip() for a in args]
    types: List[str] = [""] * len(args)

    # --- Strategy 1: Inline signature "name(type1, type2, ...)" ---
    _merge_types(types, _infer_from_inline_signature(combined, arg_names))
    if all(t for t in types):
        return types

    # --- Strategy 2: SYNOPSIS angle brackets "<type>" ---
    _merge_types(types, _infer_from_synopsis(combined, arg_names))
    if all(t for t in types):
        return types

    # --- Strategy 3: Description "param_name ... type" ---
    _merge_types(types, _infer_from_descriptions(combined, arg_names))
    if all(t for t in types):
        return types

    # --- Strategy 4: Default values ---
    _merge_types(types, _infer_from_defaults(args, arg_names))

    return types


def _merge_types(target: List[str], source: List[str]) -> None:
    """Fill empty slots in target from source."""
    for i in range(min(len(target), len(source))):
        if not target[i] and source[i]:
            target[i] = source[i]


def _infer_from_inline_signature(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from patterns like 'door.enable(bool)' or 'func(a, b, c)'."""
    types: List[str] = [""] * len(arg_names)

    # Find all patterns: identifier(type1, type2, ...)
    matches = re.findall(r"\b\w+(?:\.\w+)?\s*\(\s*([^)]*)\)", text)
    for match in matches:
        raw_types = [t.strip() for t in match.split(",") if t.strip()]
        if not raw_types:
            continue
        for i, raw in enumerate(raw_types):
            if i < len(arg_names):
                mapped = _TYPE_KEYWORDS.get(raw.lower())
                if mapped:
                    types[i] = mapped
                else:
                    types[i] = raw.lower()
        if all(t for t in types):
            break

    return types


def _infer_from_synopsis(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from SYNOPSIS angle-bracket patterns like '<type>'."""
    types: List[str] = [""] * len(arg_names)

    # Find all <type> patterns in order
    bracket_types = re.findall(r"<(\w+)>", text)
    if not bracket_types:
        return types

    for i, raw in enumerate(bracket_types):
        if i < len(arg_names):
            mapped = _TYPE_KEYWORDS.get(raw.lower())
            types[i] = mapped if mapped else raw.lower()

    return types


def _infer_from_descriptions(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from 'param_name ... type_description' patterns."""
    types: List[str] = [""] * len(arg_names)

    for name in arg_names:
        if not name:
            continue
        # Look for "param_name ... description with type keywords"
        # Pattern: name followed by ... then description
        pattern = re.escape(name) + r"\s*\.\.\.(.*?)(?=\w+\s*\.\.\.|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            desc = match.group(1)
            mapped = _extract_type_from_description(desc)
            if mapped != TYPE_UNKNOWN:
                idx = arg_names.index(name)
                types[idx] = mapped

    # Also try simple keyword scan per param name
    for name in arg_names:
        if not name or types[arg_names.index(name)]:
            continue
        # Check if the param name appears near a type keyword
        idx = arg_names.index(name)
        escaped = re.escape(name)
        # Look for "name ... keyword" within a reasonable window
        pattern = escaped + r"\s*\.\.\.(.*?)(?:\w+\s*\.\.\.|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            window = match.group(1)[:80].lower()
            for keyword, nasal_type in _TYPE_KEYWORDS.items():
                if re.search(r'\b' + re.escape(keyword) + r'\b', window):
                    types[idx] = nasal_type
                    break

    return types


def _infer_from_defaults(args: List[str], arg_names: List[str]) -> List[str]:
    """Infer types from default values: param = 0 → scalar, param = nil → nil, etc."""
    types: List[str] = [""] * len(arg_names)

    for i, arg in enumerate(args):
        if "=" not in arg:
            continue
        default_part = arg.split("=", 1)[1].strip()
        default_value = default_part.split()[0] if default_part.split() else ""

        if default_value in ("nil", "None"):
            types[i] = TYPE_NIL
        elif default_value in ("true", "false"):
            types[i] = TYPE_BOOL
        elif default_value in ("[]", "()"):
            types[i] = TYPE_VECTOR
        elif default_value in ("{}", ""):
            if default_value == "{}":
                types[i] = TYPE_HASH
        elif default_value.startswith('"') or default_value.startswith("'"):
            types[i] = TYPE_SCALAR
        elif re.match(r'^\d', default_value) or default_value in ("0", "1"):
            types[i] = TYPE_SCALAR
        elif default_value.startswith("func"):
            types[i] = TYPE_FUNC

    return types