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
    "void": TYPE_VOID,
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

    # 2. Check for @return tag
    return_tag_result = _check_return_tag(combined)
    if return_tag_result:
        return return_tag_result

    # 3. Check for Returns: block or single-line
    returns_block_result = _check_returns_block(combined)
    if returns_block_result:
        return returns_block_result

    # 4. Check for arrow patterns
    arrow_result = _check_arrow_patterns(combined)
    if arrow_result:
        return arrow_result

    # 5. Check for "returns ..." patterns
    returns_pattern_result = _check_returns_patterns(combined)
    if returns_pattern_result:
        return returns_pattern_result

    # 6. Fallback: scan for type keywords
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


def _check_return_tag(text: str) -> Optional[str]:
    """Check '@return type ...' pattern (addon framework / wiki format)."""
    m = re.search(r"@return\s+(\w+)", text)
    if m:
        keyword = m.group(1).lower()
        mapped = _TYPE_KEYWORDS.get(keyword)
        if mapped:
            return mapped
    return None


def _check_returns_block(text: str) -> Optional[str]:
    """Check 'Returns: type' single-line and block format (wiki format)."""
    # Single-line: "returns: string" or "returns: number"
    m = re.search(r"returns:\s*(\w+)", text)
    if m:
        keyword = m.group(1).lower()
        mapped = _TYPE_KEYWORDS.get(keyword)
        if mapped:
            return mapped
    return None


def infer_return_type_description(comments: List[str]) -> str:
    """Extract the return type description from comment patterns.

    Supports:
    - '@return type description' — description is everything after the type word
    - '@return description' — untyped, whole text after @return
    - 'Returns: type: description' — description is everything after 'type:'

    Args:
        comments: List of cleaned comment strings (without leading `#`).

    Returns:
        The description string, or empty string if none found.
    """
    if not comments:
        return ""

    combined = " ".join(comments)

    # Pattern 1: @return type description — type must be a known keyword
    m = re.search(r"@return\s+(\w+)\s+(.*?)(?=\s*@|\breturns:\s*\w|$)", combined, re.DOTALL | re.IGNORECASE)
    if m:
        type_word = m.group(1).lower()
        if _TYPE_KEYWORDS.get(type_word):
            return m.group(2).strip()

    # Pattern 1b: @return description — untyped fallback
    m = re.search(r"@return\s+(.*?)(?=\s*@|\breturns:\s*\w|$)", combined, re.DOTALL | re.IGNORECASE)
    if m:
        desc = m.group(1).strip()
        if desc and desc.lower() not in _TYPE_KEYWORDS:
            return desc

    # Pattern 2: Returns: type: description
    m = re.search(r"returns:\s*\w+\s*:\s*(.*)", combined, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    return ""


def infer_arg_descriptions(comments: List[str], args: List[str]) -> List[str]:
    """Extract parameter descriptions from comment patterns.

    Supports:
    - '@param type name description' — description is everything after the name
    - 'Args:' block 'name (type): description' — description is everything after ') :'

    Args:
        comments: List of cleaned comment strings.
        args: List of raw argument strings from the parser.

    Returns:
        List of description strings parallel to ``args``.  Unknown parameters
        receive an empty string.
    """
    if not comments or not args:
        return [""] * len(args)

    combined = " ".join(comments)
    arg_names = [a.split("=")[0].strip() for a in args]
    descriptions: List[str] = [""] * len(args)

    # Strategy 1: @param type name description
    _merge_descriptions(descriptions, _infer_from_param_tag_descriptions(combined, arg_names))
    if all(d for d in descriptions):
        return descriptions

    # Strategy 2: Args: block name (type): description
    _merge_descriptions(descriptions, _infer_from_args_block_descriptions(combined, arg_names))

    return descriptions


def _merge_descriptions(target: List[str], source: List[str]) -> None:
    """Fill empty slots in target from source."""
    for i in range(min(len(target), len(source))):
        if not target[i] and source[i]:
            target[i] = source[i]


def _infer_from_param_tag_descriptions(text: str, arg_names: List[str]) -> List[str]:
    """Extract descriptions from '@param' tag patterns.

    Handles both:
    - '@param type name description' (typed)
    - '@param name description' (untyped, most common in FGROOT)
    """
    descriptions: List[str] = [""] * len(arg_names)
    parts = re.split(r'\s*@param\s+', ' ' + text)
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        # Try typed pattern first: type name description
        m = re.match(r"(\w+)\s+(\w+)\s+(.*?)(?=\s*@|\Z)", part, re.DOTALL)
        if m:
            type_word, name, desc = m.group(1), m.group(2), m.group(3).strip()
            if type_word.lower() in _TYPE_KEYWORDS and name in arg_names:
                idx = arg_names.index(name)
                if desc:
                    descriptions[idx] = desc
                continue
        # Fallback: name description (or name only)
        m = re.match(r"(\w+)\s*(.*?)(?=\s*@|\Z)", part, re.DOTALL)
        if m:
            name, desc = m.group(1), m.group(2).strip()
            if name in arg_names:
                idx = arg_names.index(name)
                # Don't overwrite already-filled typed entry and don't add empty
                if not descriptions[idx] and desc:
                    descriptions[idx] = desc
    return descriptions


def _infer_from_args_block_descriptions(text: str, arg_names: List[str]) -> List[str]:
    """Extract descriptions from 'Args:' block 'name (type): description' format."""
    descriptions: List[str] = [""] * len(arg_names)
    for m in re.finditer(r"(\w+)\s*\(\w+\)\s*:\s*(.*?)(?=\s*\w+\s*\(|$)", text, re.DOTALL):
        name, desc = m.group(1), m.group(2).strip()
        if name in arg_names:
            idx = arg_names.index(name)
            descriptions[idx] = desc
    return descriptions


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
    3. @param type name format (addon framework / wiki)
    4. Args: block with (type) format (wiki)
    5. Description patterns like ``param_name ... type_description``
    6. Default-value hints from arg strings (``param = 0`` → scalar)

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

    # Strategy 1: Inline signature "name(type1, type2, ...)" 
    _merge_types(types, _infer_from_inline_signature(combined, arg_names))
    if all(t for t in types):
        return types

    # Strategy 2: SYNOPSIS angle brackets "<type>" 
    _merge_types(types, _infer_from_synopsis(combined, arg_names))
    if all(t for t in types):
        return types

    # Strategy 3: @param type name format 
    _merge_types(types, _infer_from_param_tags(combined, arg_names))
    if all(t for t in types):
        return types

    # Strategy 4: Args: block with (type) format 
    _merge_types(types, _infer_from_args_block(combined, arg_names))
    if all(t for t in types):
        return types

    # Strategy 5: Description "param_name ... type" 
    _merge_types(types, _infer_from_descriptions(combined, arg_names))
    if all(t for t in types):
        return types

    # Strategy 6: Default values 
    _merge_types(types, _infer_from_defaults(args, arg_names))

    return types


def _merge_types(target: List[str], source: List[str]) -> None:
    """Fill empty slots in target from source."""
    for i in range(min(len(target), len(source))):
        if not target[i] and source[i]:
            target[i] = source[i]


def _infer_from_param_tags(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from '@param' tag patterns.

    Handles:
    - '@param type name' (typed)
    - '@param name description' where description starts with a type word
      e.g. 'String to compare', 'Vector of 3 values'
    - '@param name ([...])' or '@param name [<...>]' → vector
    """
    types: List[str] = [""] * len(arg_names)

    # Strategy 1: typed pattern @param type name
    matches = re.findall(r"@param\s+(\w+)\s+(\w+)", text)
    for type_word, name in matches:
        mapped = _TYPE_KEYWORDS.get(type_word.lower())
        if mapped and name in arg_names:
            idx = arg_names.index(name)
            types[idx] = mapped

    # Strategy 2: infer from description prefix for remaining untyped params
    parts = re.split(r'\s*@param\s+', ' ' + text)
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        # Check if this part was already handled as typed
        m_typed = re.match(r"(\w+)\s+(\w+)\s+", part)
        if m_typed:
            type_word, name = m_typed.group(1), m_typed.group(2)
            if type_word.lower() in _TYPE_KEYWORDS and name in arg_names:
                continue  # already handled
        # Untyped: name + description
        m = re.match(r"(\w+)\s*(.*)", part, re.DOTALL)
        if not m:
            continue
        name, desc = m.group(1), m.group(2).strip()
        if name not in arg_names:
            continue
        idx = arg_names.index(name)
        if types[idx]:
            continue
        # Bracket/paren vector hint like ([width, height]) or [<x>, <y>]
        if desc.strip().startswith(("(", "[")):
            types[idx] = TYPE_VECTOR
            continue
        desc_stripped = desc.lstrip(" ([{<")
        # First word of description as type hint
        first_word_m = re.match(r"([A-Za-z]+)", desc_stripped)
        if first_word_m:
            first_word = first_word_m.group(1).lower()
            # Direct keyword match
            mapped = _TYPE_KEYWORDS.get(first_word)
            if mapped:
                types[idx] = mapped
                continue
            # Fallback: scan description for any type keyword
            # e.g. "Optional hash of options" → hash
            mapped = _extract_type_from_description(desc)
            if mapped != TYPE_UNKNOWN:
                types[idx] = mapped

    return types


def _infer_from_args_block(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from 'Args:' block with '(type)' format (wiki)."""
    types: List[str] = [""] * len(arg_names)
    matches = re.findall(r"(\w+)\s*\((\w+)\)", text)
    for name, type_word in matches:
        if name not in arg_names:
            continue
        mapped = _TYPE_KEYWORDS.get(type_word.lower())
        if mapped:
            idx = arg_names.index(name)
            types[idx] = mapped
    return types


def _infer_from_inline_signature(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from patterns like 'door.enable(bool)' or 'func(a, b, c)'."""
    types: List[str] = [""] * len(arg_names)

    # Find all patterns: name(type1, type2, ...)
    matches = re.findall(r"\b(\w+)(?:\.\w+)?\s*\(\s*([^)]*)\)", text)
    for name, match_str in matches:
        if name not in arg_names:
            continue
        raw_types = [t.strip() for t in match_str.split(",") if t.strip()]
        if not raw_types:
            continue
        idx = arg_names.index(name)
        for i, raw in enumerate(raw_types):
            if idx + i < len(arg_names):
                mapped = _TYPE_KEYWORDS.get(raw.lower())
                if mapped:
                    types[idx + i] = mapped
                # Unknown raw types (e.g. "[width") are ignored to avoid polluting
        if all(t for t in types):
            break

    return types


def _infer_from_synopsis(text: str, arg_names: List[str]) -> List[str]:
    """Extract types from SYNOPSIS angle-bracket patterns like '<type>'."""
    types: List[str] = [""] * len(arg_names)

    if "synopsis" not in text.lower():
        return types

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