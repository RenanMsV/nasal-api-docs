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

"""HTML generator tests for the nasal_api_docs package."""

import json
from nasal_api_docs import NasalAPI, parser


def test_basic_generation(nasal_api: NasalAPI):
    """Test that the API can read fg_version and generate documentation."""
    version = nasal_api.get_fg_version()
    assert version.startswith("9797"), "Incorrect or missing FG version"

    html_path = nasal_api.generate_html()
    json_path = nasal_api.generate_json_tree()

    assert html_path.exists(), "HTML output file not created"
    assert json_path.exists(), "JSON output file not created"


def test_html_generation(nasal_api: NasalAPI):
    """Test that the API generated a reasonable enough html."""
    html_path = nasal_api.generate_html()

    assert html_path.exists(), "HTML output file not created"

    with open(html_path, "r", encoding="utf-8") as file:
        data = file.read()

        assert "<title>Nasal API - 9797.1.0</title>" in data, "Incorrect title."

        assert "FlightGear version: 9797.1.0 .<br/>" in data, "Incorrect FG version."

        assert (
            "<a target=\"_blank\" href=\""
            "http://plausible.org/nasal\">Plausible.org</a>"
        ) in data, "Missing link buttons."

        assert (
            "<a class=\"main_module_link\" href="
            "\"#aircraft.nas\">&#128196; aircraft</a>"
        ) in data, "Incorrect module link in right namespace menu."

        assert (
            "<a name=\"aircraft.nas\">&#128196; aircraft</a>"
        ) in data, "Incorrect namespace title."

        assert (
            "<span class=\"rel_path\">&nbsp;&nbsp;&nbsp;&nbsp;"
            "Nasal/aircraft.nas</span>"
        ) in data, "Incorrect path of Nasal file."

        assert (
            "<b>aircraft</b>.<b>makeNode</b> ( <span class=\"arg\">n</span>, "
            "<span class=\"arg\">anotherArgument</span> )"
        ) in data, "Incorrect function name and parameters."

        assert (
            "<div class=\"comments\">This is a comment first line</div><br/>"
        ) in data, "Incorrect comment."

        assert (
            "<div class=\"comments\">This is a comment third line</div><br/>"
        ) in data, "Incorrect comment."


def test_json_generation(nasal_api: NasalAPI):
    """Test that the API generated a reasonable enough json."""
    json_path = nasal_api.generate_json_tree()

    assert json_path.exists(), "JSON output file not created"

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

        assert data["meta"], "Missing metadata"

        assert data["meta"]["fg_version"].startswith("9797"), (
            "Incorrect or missing FG version."
        )

        assert data["meta"]["parser_version"] == parser.NasalParser.VERSION_STR, (
            "Incorrect parser version."
        )
