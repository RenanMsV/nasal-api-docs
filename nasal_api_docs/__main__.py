#!/usr/bin/env python3

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
Main entry point for the Nasal API documentation generator.

Parses FlightGear Nasal scripts and generates documentation in multiple formats.
Supports command-line arguments for FlightGear data folder and output path.

Usage:
    python -m nasal_api_docs -f /path/to/fgdata/ -o ./out
"""

import argparse
import sys
from pathlib import Path
from mkdocs.config import load_config as mkdocs_load_config  # type: ignore
from mkdocs.commands.build import build as mkdocs_build

from nasal_api_docs import NasalAPI
from .logger import get_logger

DEFAULT_NASAL_PATH = None
DEFAULT_OUTPUT_PATH = Path("./out")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="nasal-api-docs",
        description=(
            "Auto-generate Nasal API documentation from FlightGear Nasal scripts."
        )
    )
    parser.add_argument(
        "-f",
        metavar="PATH",
        help="Path to the FlightGear Data folder.",
        required=True
    )
    parser.add_argument(
        "-o",
        metavar="PATH",
        help=f"Output folder (default: {DEFAULT_OUTPUT_PATH}).",
        default=str(DEFAULT_OUTPUT_PATH),
    )
    parser.add_argument(
        "--html",
        action="store_true",
        dest="html",
        help="Will output a generated html file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json",
        help="Will output a generated json file.",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        dest="markdown",
        help="Will output generated markdown files (MkDocs).",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        dest="build",
        help=(
            "Will build files if necessary. "
            "Useful if you need to build: [MkDocs, ...]"
        ),
    )

    args = parser.parse_args(argv)
    return args


def main(argv: list[str] | None = None) -> int:
    """Runs the Nasal API documentation generator."""
    logger = get_logger()

    args = _parse_args(argv or sys.argv[1:])
    fg_root_dir = Path(args.f)
    output_dir = Path(args.o)
    should_output_all = not any([
        args.html,
        args.json,
        args.markdown,
    ])

    try:
        nasal_api = NasalAPI(fg_root_dir, output_dir)

        fg_version = nasal_api.get_fg_version()
        logger.info("Generating outputs for FlightGear version %s", fg_version)

        if should_output_all or args.html:
            html_file = nasal_api.generate_html()
            logger.info("Generated HTML file at %s", html_file)

        if should_output_all or args.json:
            json_file = nasal_api.generate_json_tree()
            logger.info("Generated JSON tree at %s", json_file)

        if should_output_all or args.markdown:
            markdown_out_dir = nasal_api.generate_markdown()
            logger.info("Generated MARKDOWN files at %s", markdown_out_dir)

        if args.build:
            mkdocs_config = mkdocs_load_config()
            # Replace $fg_version in the mkdocs_config with the FlightGear version
            mkdocs_config.site_name = mkdocs_config.site_name.replace(
                "$fg_version",
                fg_version
            )
            # Modify site and docs dir to be inside the output_dir to respect -o arg
            mkdocs_config.site_dir = str(output_dir / "mkdocs" / "site")
            mkdocs_config.docs_dir = str(output_dir / "mkdocs" / "docs")
            logger.info("Building MARKDOWN with MkDocs at %s", mkdocs_config.site_dir)
            mkdocs_build(mkdocs_config)

    except FileNotFoundError as e:
        logger.error("Missing file or directory: %s", e)
        raise
    except ValueError as e:
        logger.error("Invalid value: %s", e)
        raise
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Unexpected error: %s", e)
        raise

    return 0


if __name__ == "__main__":
    sys.exit(main())
