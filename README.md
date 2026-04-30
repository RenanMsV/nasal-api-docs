# Nasal API Docs

<p align="center">
    <img src="https://i.imgur.com/Y0ds1jD.png"
        height="130">
</p>
<p align="center">
    <a href="https://pypi.org/project/nasal-api-docs/" alt="pypi status">
        <img src="https://img.shields.io/pypi/status/nasal-api-docs" /></a>
    <a href="https://github.com/RenanMsV/nasal-api-docs/" alt="gh tests status">
        <img src="https://img.shields.io/github/actions/workflow/status/RenanMsV/nasal-api-docs/tests.yml" /></a>
    <a href="https://pypi.org/project/nasal-api-docs/" alt="pypi version">
        <img src="https://img.shields.io/pypi/v/nasal-api-docs" /></a>
    <a href="https://pypi.org/project/nasal-api-docs/" alt="pypi implementation">
        <img src="https://img.shields.io/pypi/implementation/nasal-api-docs" /></a>
    <a href="https://pypi.org/project/nasal-api-docs/" alt="pypi license">
        <img src="https://img.shields.io/pypi/l/nasal-api-docs" /></a>
</p>

Auto generates Nasal API documentation from FlightGear's nasal scripts.

* Original python2 script by Adrian Musceac @2012.
* Refactored into a package by RenanMsV @2019-2026.

---

### Latest generated docs

📃 View the latest docs here: [nasal-api-docs/latest](https://renanmsv.github.io/nasal-api-docs/latest).

---

### Requirements

- Requires **Python 3.7** or newer.

- Uses [Jinja2](https://pypi.org/project/Jinja2/) module to generate the HTML.
To install Jinja2 run the console command below:
    ```bash
    pip install jinja2
    ```

---

### How to install and run:

🧩 This project is published at <https://pypi.org/project/nasal-api-docs>

Install it with:
```bash
pip install nasal-api-docs
```

Run the command:
```bash
nasal-api-docs -f /path/to/FlightGear/data -o /path/to/output/
```

The output files will be generated and saved to the output path specified in the command.

For more help check our [wiki](https://github.com/RenanMsV/nasal-api-docs/wiki).
