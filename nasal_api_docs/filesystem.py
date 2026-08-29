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

"""Filesystem utilities for the Nasal API documentation generator.

Provides representations for Nasal source files and functions, as well as
recursive scanning and version detection for FlightGear data trees.

Classes:
    NasalFunction: Represents a Nasal function or class.
    NasalItem: Represents a file or module in the Nasal hierarchy.
    NasalFileSystem: Scans the file system and builds the in-memory tree.
"""

from __future__ import annotations
from dataclasses import dataclass, field


from pathlib import Path
from typing import Any, Dict, List

from .parser import NasalParser
from .type_inference import infer_return_type
from .logger import get_logger
logger = get_logger()


@dataclass
class NasalFunction:
    """Represents a Nasal function with name, args, and comments."""
    name: str
    args: List[str]
    comments: List[str]
    type: str = ""      # computed in __post_init__
    return_type: str = ""  # computed in __post_init__

    def __post_init__(self):
        self.type = "class_definition" if self.name.endswith(".") else "function"
        self.name = self.name.rstrip(".")
        self.return_type = infer_return_type(self.comments)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this object to a dictionary suitable for JSON.

        Returns:
            dict: The object as a dict.
        """
        return {
            "type": self.type,
            "name": self.name,
            "args": self.args,
            "comments": self.comments,
            "return_type": self.return_type,
        }


@dataclass
class NasalItem:
    """Represents a file or module in the Nasal hierarchy."""
    name: str
    path: Path
    root_path: Path
    is_module: bool = False
    children: list["NasalItem"] = field(default_factory=lambda: [])  # submodules
    functions: list["NasalFunction"] = field(default_factory=lambda: [])  # files
    icon: str = ""          # computed in __post_init__
    rel_path: str = ""      # computed in __post_init__
    id: str = ""            # computed in __post_init__
    type: str = ""          # computed in __post_init__

    def __post_init__(self):
        self.icon = "&#128193;" if self.is_module else "&#128196;"  # 📁, 📄
        self.rel_path = (
            (
                "Nasal\\"
                + str((self.path / self.name).relative_to(self.root_path))
                + ("\\" if self.is_module else ".nas")
            )
            .replace("\\", "/")
        )
        self.id = self.rel_path[6:].lower().replace("/", "_").rstrip("_")
        logger.info("Found Nasal item: %s, id: %s", self.rel_path, self.id)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this object to a dictionary suitable for JSON.

        Returns:
            dict: The object as a dict.
        """
        return {
            "name": self.name,
            "path": str(self.path),
            "rel_path": self.rel_path,
            "is_module": self.is_module,
            "icon": self.icon,
            "functions": [
                f.to_dict()
                for f in self.functions
            ],
            "children": [child.to_dict() for child in self.children],
        }


class NasalFileSystem:
    """_summary_
    """
    _parser: NasalParser = NasalParser()
    nasal_tree: List[NasalItem]
    nasal_dir: Path
    fg_root_dir: Path
    fg_version: str

    def __init__(self, fg_root_dir: Path):
        """Inits the Nasal file system."""
        self.fg_root_dir = fg_root_dir
        self.nasal_dir = fg_root_dir / "Nasal"
        self.fg_version = self._read_fg_version()
        self.nasal_tree = self._get_nasal_tree()

    def _read_fg_version(self) -> str:
        """Read FlightGear version string from the $FGROOT 'version' file."""
        version_file = self.fg_root_dir / "version"
        if not version_file.exists():
            raise FileNotFoundError("Version file not found in $FGROOT")
        with version_file.open("r", encoding="utf-8", errors="replace") as f:
            self.fg_version = f.read(256).rstrip("\n")
            return self.fg_version

    def _get_nasal_tree(self) -> List[NasalItem]:
        """
        Scan the nasal_dir recursively and return a list of NasalItems (files/modules).
        """
        self.nasal_dir = self.nasal_dir.resolve()
        if not self.nasal_dir.exists():
            raise FileNotFoundError(f"Path does not exist: {self.nasal_dir}")

        def scan_dir(path: Path) -> List[NasalItem]:
            items: List[NasalItem] = []
            for entry in sorted(path.iterdir()):
                if entry.is_file() and entry.suffix == ".nas":
                    file_item = NasalItem(
                        name=entry.stem,
                        path=path,
                        root_path=self.nasal_dir
                    )
                    # Convert tuples from parse_file() to NasalFunction objects
                    file_item.functions = [
                        NasalFunction(
                            name=f[0],
                            args=[a.strip() for a in f[1].split(',') if a.strip()],
                            comments=f[2]
                        )
                        for f in self._parser.parse_file(entry)
                    ]
                    items.append(file_item)
                elif entry.is_dir():
                    module_item = NasalItem(
                        name=entry.name,
                        is_module=True,
                        path=path,
                        root_path=self.nasal_dir
                    )
                    # Recursively scan subfolder
                    module_item.children = scan_dir(entry)
                    items.append(module_item)
            return items

        return scan_dir(self.nasal_dir)
