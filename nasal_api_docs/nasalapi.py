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

"""Nasal API main interface.

This module provides a high-level object-oriented interface for parsing
FlightGear Nasal scripts and generating documentation in multiple formats.

Classes:
    NasalAPI: Main entry point for interacting with the Nasal parser, filesystem,
    and documentation generators.
"""

from pathlib import Path

from .generator import NasalDocsGenerator
from .parser import NasalParser
from .filesystem import NasalFileSystem


class NasalAPI:
    """High-level interface for the Nasal documentation generator.

    This class serves as the main entry point to interact with the package.
    It encapsulates:
        - File discovery and parsing via NasalFileSystem
        - Documentation generation via NasalDocsGenerator
        - Access to FlightGear metadata such as version and structure

    Attributes:
        fg_root_dir (Path): Path to the FlightGear root data directory ($FG_ROOT).
        output_dir (Path): Directory where output files will be written.
    """

    _file_system: NasalFileSystem
    _generator: NasalDocsGenerator
    _parser: NasalParser

    fg_root_dir: Path
    output_dir: Path

    def __init__(self, fg_root_dir: Path, output_dir: Path):
        """Initialize the Nasal API interface.

        Args:
            fg_root_dir (Path): The FlightGear root data directory.
            output_dir (Path): The directory to output generated documentation files.
        """
        self.fg_root_dir = fg_root_dir
        self.output_dir = output_dir

        self._file_system = NasalFileSystem(self.fg_root_dir)
        self._generator = NasalDocsGenerator(self._file_system, self.output_dir)

    def get_fg_version(self) -> str:
        """Return the FlightGear version detected from $FG_ROOT."""
        return self._file_system.fg_version

    def generate_html(self):
        """Generate the Nasal API documentation in HTML format.

        Returns:
            Path: The path of the generated HTML file.
        """
        return self._generator.generate_html()

    def generate_json_tree(self):
        """Generate the Nasal API tree in JSON format.

        Returns:
            Path: The path of the generated JSON file.
        """
        return self._generator.generate_json_tree()

    def generate_markdown(self):
        """Generate the Nasal API documentation in Markdown format.

        Returns:
            Path: The path of the generated Markdown file.
        """
        return self._generator.generate_markdown()

    def generate_csv(self):
        """Generate the Nasal API documentation in CSV format.

        Returns:
            Path: The path of the generated CSV file.
        """
        return self._generator.generate_csv()

    def generate_all(self):
        """Generate all supported documentation formats.

        Returns:
            list[Path]: List of all generated file paths.
        """
        return self._generator.generate_all()
