# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2025-03-31

### Fixed
- Improved API key handling with support for both GOOGLE_API_KEY and GEMINI_API_KEY
- Added clear error messages when API key is missing
- Updated README with consistent uv commands and correct GitHub URLs

## [0.4.1] - 2025-03-31

### Changed
- Updated README with improved quickstart commands
- Updated environment variable references from GEMINI_API_KEY to GOOGLE_API_KEY
- Enhanced CONTRIBUTING.md with detailed release instructions

## [0.2.0] - 2025-03-31

### Changed
- Refactored code structure
- Improved LLM integration
- Added debugging utilities

## [0.1.0] - 2025-03-15

### Added
- Initial release of AILabel
- CLI for managing topics and labels
- Label prediction using Google Gemini API
- Unix-style CLI with stdin/stdout support
- Batch processing for multi-line inputs
- Comprehensive test suite
- Documentation and example usage