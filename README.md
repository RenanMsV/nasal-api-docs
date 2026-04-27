# Nasal API Docs

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

Install with:
```bash
pip install .
```

Run the command:
```bash
nasal-api-docs -f /path/to/FlightGear/data -o /path/to/output/
```
