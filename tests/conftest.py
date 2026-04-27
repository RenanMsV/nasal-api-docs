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

"""Shared pytest configuration and fixtures for nasal_api_docs tests."""

from pathlib import Path
import pytest

from nasal_api_docs import NasalAPI


@pytest.fixture(scope="session")
def fg_root_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Provides a temporary fake FlightGear root directory with the minimal structure
    required by tests.

    The layout will be:
        tmp/
        ├── fgdata/
        │   └── Nasal/
        └── output/

    Returns:
        Path: The path to the created fgdata directory (used as fg_root_dir).
    """
    tmp_root = tmp_path_factory.mktemp("tmp")

    # Create folder structure
    fg_dir = tmp_root / "fgdata"
    nasal_dir = fg_dir / "Nasal"

    fg_dir.mkdir(parents=True, exist_ok=True)
    nasal_dir.mkdir(parents=True, exist_ok=True)

    # Create a fake FlightGear version file
    (fg_dir / "version").write_text("9797.1.0", encoding="utf-8")

    # Create a small fake .nas file
    (nasal_dir / "aircraft.nas").write_text(
        "# This is a comment first line\n"
        "# \n"
        "# This is a comment third line\n"
        "#\n"
        "var makeNode = func(n, anotherArgument) {\n"
        "\tif (isa(n, props.Node))\n"
        "\t\treturn n;\n"
        "\telse\n"
        "\t\treturn props.globals.getNode(n, 1);\n"
        "}\n",
        encoding="utf-8",
    )

    return fg_dir


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Provides a temporary output directory for generated documentation.

    Returns:
        Path: The path to the created temporary output directory.
    """
    # Let pytest handle temp directory creation and cleanup
    out_dir = tmp_path_factory.mktemp("output")
    return out_dir


@pytest.fixture(scope="session")
def nasal_api(fg_root_dir: Path, output_dir: Path) -> NasalAPI:  # pylint: disable=W0621
    """Provides a ready-to-use NasalAPI instance for all tests."""
    return NasalAPI(fg_root_dir=fg_root_dir, output_dir=output_dir)
