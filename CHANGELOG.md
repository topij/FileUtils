# Changelog

## [0.8.5] - 2025-11-30

### Added
- **Logging Control**: New `quiet` parameter to suppress all logging except CRITICAL errors
- **Enhanced Log Level Support**: `log_level` parameter now accepts both string ("INFO") and logging constants (logging.INFO)
- **Parameter Priority**: `log_level` > `quiet` > default (INFO) for flexible control
- **Clean Output Mode**: Support for automation, CI/CD, and structured output (JSON/XML) scenarios

### Changed
- Updated `setup_logger` to accept both string and integer log levels
- Enhanced `FileUtils.__init__` docstring with logging control examples

### Documentation
- Added "Logging Control" section to README
- Added comprehensive test suite for logging features
