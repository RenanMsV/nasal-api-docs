# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-04-27

### Added

- Latest generated docs is now deployed to [nasal-api-docs/latest](https://renanmsv.github.io/nasal-api-docs/latest).
- Made this project into a package.
- Added [Changelog](CHANGELOG.md).
- Better logging.

### Changed

- New `dev` branch contains all unreleased changes. Now the main branch only gets updated when releases happen.
- Reworked structure and layout (html, css).
- Tweaking the parser.
- Now it outputs a json file together with the HTML file.

### Removed

- Archives folder deleted. They have been moved to the [deployment branch](https://github.com/RenanMsV/nasal-api-docs/tree/docs).

## [0.1.2] - 2025-10-15

### Added

- Add output path argument.

### Changed

- Archiving 2019.1.1 docs.
- Update readme with instructions.
- Use argparse to manage arguments.
- Outputs fg version and datetime in the HTML.

### Removed

- Drop support for Python 2 script.

## [0.1.1] - 2019-10-2

### Changed

- Renamed `./python/*` -> `./*`.

## [0.1.0] - 2019-08-10

### Added

- Initial commit.
- Added LICENSE and README.

### Changed

- Converted from Python 2.7 to 3.6; -Output size is bigger.

[unreleased]: https://github.com/RenanMsV/nasal-api-docs/compare/master...dev
[0.2.0]: https://github.com/RenanMsV/nasal-api-docs/releases/tag/0.2.0
[0.1.2]: https://github.com/RenanMsV/nasal-api-docs/releases/tag/0.1.2
[0.1.1]: https://github.com/RenanMsV/nasal-api-docs/releases/tag/0.1.1
[0.1.0]: https://github.com/RenanMsV/nasal-api-docs/releases/tag/0.1.0