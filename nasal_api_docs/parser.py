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

"""Nasal parser for FlightGear scripts.

This module uses regular expressions to extract documentation-relevant
constructs from Nasal source files.

Extracts:
    - Function definitions (top-level and member functions)
    - Class declarations
    - Dot-assigned functions (Class.func = func(...))
    - Comments immediately preceding definitions

Returns:
    list[tuple[str, str, list[str]]]: A structured list of definitions,
    each containing the symbol name, parameter string, and preceding comments.
"""

import re
from pathlib import Path
from typing import List, Tuple


# Regex patterns
_RE_VAR_CLASS = re.compile(r"^var\s*([A-Za-z0-9_-]+)\s*=\s*{\s*(\n|})")
_RE_VAR_FUNC = re.compile(
    r"^var\s+([A-Za-z0-9_-]+)\s*=\s*func\s*\(?([A-Za-z0-9_\s,=.\n-]*)\)?"
)
_RE_MEMBER_FUNC = re.compile(
    r"^\s*([A-Za-z0-9_-]+)\s*:\s*func\s*\(?([A-Za-z0-9_\s,=.\n-]*)\)?"
)
_RE_DOT_FUNC = re.compile(
    r"^([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\s*=\s*func\s*\(?([A-Za-z0-9_\s,=\n.-]*)\)?"
)


class NasalParser:
    """Parse Nasal source files into structured documentation data."""

    VERSION = (1, 0, 0)
    VERSION_STR = "1.0.0"

    _CHANGELOG = {
        (1, 0, 0): "Initial release"
    }

    @classmethod
    def version_info(cls) -> str:
        """Returns the Parser version info as a string."""
        notes = cls._CHANGELOG.get(cls.VERSION, "")
        return f"Parser v{cls.VERSION_STR} — {notes}"

    def parse_file(self, filename: Path) -> List[Tuple[str, str, List[str]]]:
        """Parse a Nasal source file.

        Args:
            filename (Path): Path to the Nasal (.nas) source file.

        Returns:
            list[tuple[str, str, list[str]]]: A list of tuples containing:
                - The symbol name (e.g. class.func)
                - The raw parameter list string
                - The preceding comment lines
        """
        with filename.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        result: List[Tuple[str, str, List[str]]] = []
        classname = ""

        for i, line in enumerate(lines):
            # var func
            match = _RE_VAR_FUNC.match(line)
            if match:
                func_name = match.group(1)
                param = self._expand_multiline_params(lines, i, match.group(2))
                comments = self._collect_comments(lines, i)
                result.append((func_name, param, comments))
                continue

            # var class
            match = _RE_VAR_CLASS.match(line)
            if match:
                classname = match.group(1)
                comments = self._collect_comments(lines, i)
                result.append((classname + ".", "", comments))
                continue

            # member func inside class
            match = _RE_MEMBER_FUNC.match(line)
            if match and classname:
                func_name = match.group(1)
                param = self._expand_multiline_params(lines, i, match.group(2))
                comments = self._collect_comments(lines, i)
                result.append((classname + "." + func_name, param, comments))
                continue

            # dot function: Class.func = func(...)
            match = _RE_DOT_FUNC.match(line)
            if match:
                classname = match.group(1)
                func_name = match.group(2)
                param = self._expand_multiline_params(lines, i, match.group(3))
                comments = self._collect_comments(lines, i)
                result.append((classname + "." + func_name, param, comments))
                continue

        return result

    def _expand_multiline_params(self, lines: list[str], index: int, param: str) -> str:
        """Expand parameter lists that span multiple lines.

        Args:
            lines (list[str]): The source file lines.
            index (int): The current line index where parsing started.
            param (str): The initial parameter string captured.

        Returns:
            str: The complete parameter string.
        """
        if "(" in lines[index] and ")" not in lines[index]:
            k = index + 1
            while k < len(lines) and ")" not in lines[k]:
                param += lines[k].rstrip("\n")
                k += 1
            if k < len(lines):
                param += lines[k].split(")")[0]
        return param

    def _collect_comments(self, lines: list[str], index: int) -> list[str]:
        """Collect contiguous preceding comments above a line.

        Scans backward from the given index and collects lines that start with `#`,
        skipping up to 128 blank lines or 255 total lines.

        Args:
            lines (list[str]): The source file lines.
            index (int): Index of the current definition line.

        Returns:
            list[str]: Cleaned comment lines in correct order.
        """
        comments: list[str] = []
        empty_count = 0

        for j in range(index - 1, max(index - 255, -1), -1):
            line = lines[j]
            stripped = line.strip()

            if len(stripped) < 2:
                empty_count += 1
                if empty_count > 128:
                    break
                continue

            if stripped.startswith("#"):
                clean_comment = stripped.lstrip("#").strip()
                if clean_comment:
                    comments.append(clean_comment)
            else:
                break

        if len(comments) > 1:
            comments.reverse()

        return comments
