<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.1/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.1.0] - 2026-04-26

### Added

- Man page for `mkwineprefix`.

### Changed

- Switched HTTP library from `requests` to `niquests`.
- Converted all library code from synchronous to asynchronous using `asyncio`, `anyio.Path`, and
  `asyncio.create_subprocess_exec`.
- `create_wine_prefix()` is now an `async` function. Callers must `await` it or run it inside an
  event loop.
- Use `asyncio.gather()` for concurrent subprocess and I/O operations.

### Fixed

- Raise `RuntimeError` with a clear message when Q4Wine prefix registration does not return a
  database row ID.

## [0.0.1] - 2026-02-28

First version, migrated from Deltona.

[unreleased]: https://github.com/Tatsh/mkwineprefix/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Tatsh/mkwineprefix/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/Tatsh/mkwineprefix/releases/tag/v0.0.1
