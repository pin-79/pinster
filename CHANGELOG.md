# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Running the game is now done through `pinster play`. Just `pinster` will not work
    anymore.

## [0.1.1] - 2025-02-05

### Fixed

- Store logs and cache in consistent directories, fixing the issue with trying to create
    the files in not existing dirs (#3).
- Mask Spotify Bearer token in logs (#3).

## [0.1.0] - 2025-02-04

### Added

- A simple working version: shuffle the user's Liked Songs and give room to guess
the details (#2).

[unreleased]: https://github.com/pin-79/pinster/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pin-79/pinster/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pin-79/pinster/releases/tag/v0.1.0
