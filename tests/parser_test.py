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

"""Unit tests for the NasalParser."""

from pathlib import Path
from typing import List, Tuple

from nasal_api_docs.parser import NasalParser


def test_parse_basic_var_function(tmp_path: Path) -> None:
    """
    Verify that the parser can detect a simple Nasal function definition.

    Example: var foo = func(...)

    Ensures:
        - One function definition is detected.
        - Function name and parameters are parsed correctly.
        - Correct comments are attached to the parsed result.
    """
    file: Path = tmp_path / "simple_var_function.nas"
    file.write_text(
        "# hello this is a comment\n"
        "#\n"
        "var foo = func(a, b) {\n \n\treturn a + b; \n}\n",
        encoding="utf-8"
    )

    parser: NasalParser = NasalParser()
    result: List[Tuple[str, str, List[str]]] = parser.parse_file(file)

    assert len(result) == 1, "Expected one function definition."

    name: str
    params: str
    comments: List[str]
    name, params, comments = result[0]

    assert name == "foo", "Expected name to be 'foo'."
    assert params == "a, b", "Missing or invalid params."
    assert comments == ["hello this is a comment"], (
        "Expected comments to be a single line. "
        "The empty comment line should have been ignored."
    )


def test_parse_basic_dot_function(tmp_path: Path) -> None:
    """
    Verify that the parser can detect a simple Nasal dot function definition.

    Example: Class.func = func(...)

    Ensures:
        - One function definition is detected.
        - Function name and parameters are parsed correctly.
        - Correct comments are attached to the parsed result.
    """
    file: Path = tmp_path / "simple_dot_function.nas"
    file.write_text(
        "# hello this is a comment\n"
        "#\n"
        "Class.new = func(a, b) {\n"
        "    return a + b;\n"
        "}\n",
        encoding="utf-8"
    )

    parser: NasalParser = NasalParser()
    result: List[Tuple[str, str, List[str]]] = parser.parse_file(file)

    assert len(result) == 1, "Expected one function definition."

    name: str
    params: str
    comments: List[str]
    name, params, comments = result[0]

    assert name == "Class.new", "Expected name to be 'Class.new'."
    assert params == "a, b", "Missing or invalid params."
    assert comments == ["hello this is a comment"], (
        "Expected comments to be a single line. "
        "The empty comment line should have been ignored."
    )


def test_parse_basic_var_class(tmp_path: Path) -> None:
    """
    Verify that the parser can detect a simple Nasal var class definition.

    Example: var Class = {...}

    Ensures:
        - One class definition is detected.
        - Class name is parsed correctly.
        - Correct comments are attached to the parsed result.
    """
    file: Path = tmp_path / "simple_var_class.nas"
    file.write_text(
        "# hello this is a comment\n"
        "#\n"
        "var Class = {\n"
        "}\n",
        encoding="utf-8"
    )

    parser: NasalParser = NasalParser()
    result: List[Tuple[str, str, List[str]]] = parser.parse_file(file)

    assert len(result) == 1, "Expected one function definition."

    name: str
    params: str
    comments: List[str]
    name, params, comments = result[0]

    assert name == "Class.", "Expected name to be 'Class.'."
    assert params == "", "Expected no parameters."
    assert comments == ["hello this is a comment"], (
        "Expected comments to be a single line. "
        "The empty comment line should have been ignored."
    )


def test_parse_basic_member_function(tmp_path: Path) -> None:
    """
    Verify that the parser can detect a simple Nasal member function definition.

    Example: var Class = { init: func {...}}

    Ensures:
        - One class and one member function definition are detected.
        - Class and member function name is parsed correctly.
        - Correct comments are attached to the parsed result.
    """
    file: Path = tmp_path / "simple_member_function.nas"
    file.write_text(
        "# hello this is a comment\n"
        "#\n"
        "var Class = {\n"
        "# hello this is a comment\n"
        "#\n"
        "\tinit: func (a, b) {}\n"
        "}\n",
        encoding="utf-8"
    )

    parser: NasalParser = NasalParser()
    result: List[Tuple[str, str, List[str]]] = parser.parse_file(file)

    assert len(result) == 2, "Expected two definitions."

    member_name: str
    member_params: str
    member_comments: List[str]
    member_name, member_params, member_comments = result[1]

    assert member_name == "Class.init", "Expected name to be 'Class.init'."
    assert member_params == "a, b", "Missing or invalid params."
    assert member_comments == ["hello this is a comment"], (
        "Expected comments to be a single line. "
        "The empty comment line should have been ignored."
    )
