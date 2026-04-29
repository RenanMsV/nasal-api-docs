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

"""Documentation generator for Nasal API.

This module uses Jinja2 templates and structured data from NasalFileSystem
to produce various output formats such as HTML, JSON, Markdown, and CSV.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List
from platform import python_version as pl_python_version

from jinja2 import Environment, FileSystemLoader, select_autoescape
from . import __version__  # pylint: disable=cyclic-import
from .filesystem import NasalFileSystem
from .parser import NasalParser

TEMPLATE_DIR = Path(__file__).parent / "templates"


class NasalDocsGenerator:
    """Generate Nasal API documentation files in multiple formats.

    Attributes:
        file_system (NasalFileSystem): Access to parsed Nasal tree and metadata.
        output_dir (Path): Destination folder for generated documentation files.
    """

    _file_system: NasalFileSystem
    output_dir: Path

    def __init__(self, file_system: NasalFileSystem, output_dir: Path):
        """Initialize the documentation generator."""
        self._file_system = file_system
        self.output_dir = output_dir

    def _get_timestamp_str(self) -> str:
        """Return a formatted timestamp for output metadata."""
        return datetime.now().strftime("%m-%d-%Y %I-%M-%S%p")

    def generate_all(self) -> List[Path]:
        """Generate all supported documentation formats.

        Returns:
            list[Path]: Paths of all generated output files.
        """
        files: List[Path] = []
        files.append(self.generate_html())
        files.append(self.generate_json_tree())
        return files

    def generate_html(self) -> Path:
        """Generate the HTML documentation file from the Nasal tree.

        Returns:
            Path: The generated HTML file path.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_file = (
            self.output_dir / f"nasal_api_doc-{self._file_system.fg_version}.html"
        )
        timestamp = self._get_timestamp_str()
        package_version = __version__
        parser_version = NasalParser.VERSION_STR
        python_version = pl_python_version()

        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR / "html"),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("docs_html_template.j2")
        html_content = template.render(
            fg_version=self._file_system.fg_version,
            version=package_version,
            parser_version=parser_version,
            python_version=python_version,
            timestamp=timestamp,
            tree=self._file_system.nasal_tree,
        )

        out_file.write_text(html_content, encoding="utf-8")
        return out_file

    def generate_json_tree(self):
        """Generate a JSON representation of the Nasal API tree.

        Returns:
            Path: Path to the generated JSON file.
        """
        filename = f"json_tree-{self._file_system.fg_version}.json"
        path = self.output_dir / filename
        with path.open("w", encoding="utf-8") as f:
            timestamp = self._get_timestamp_str()
            fg_version = self._file_system.fg_version
            package_version = __version__
            parser_version = NasalParser.VERSION_STR
            python_version = pl_python_version()
            json.dump(
                {
                    "meta": {
                        "timestamp": timestamp,
                        "package_version": package_version,
                        "parser_version": parser_version,
                        "fg_version": fg_version,
                        "python_version": python_version
                    },
                    "data": [item.to_dict() for item in self._file_system.nasal_tree],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        return path

    def generate_markdown(self):
        """Generate Markdown documentation (not yet implemented)."""

    def generate_csv(self):
        """Generate CSV documentation (not yet implemented)."""
