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

"""
Nasal API Docs
==============

A Python package for parsing and generating documentation for FlightGear Nasal scripts.

Typical usage example:
    from nasal_api_docs import NasalAPI

    nasal_api = NasalAPI(fg_root_dir="/path/to/FGRoot", output_dir="output/")
    nasal_api.generate_all()
    nasal_api.generate_html()
"""

# nasal_api_docs/__init__.py
from importlib.metadata import version

__version__ = version("nasal_api_docs")

from .nasalapi import NasalAPI
from .logger import get_logger

logger = get_logger()

__all__ = ["NasalAPI", "logger"]
