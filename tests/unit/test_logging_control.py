# tests/unit/test_logging_control.py

import io
import logging
import sys

from FileUtils import FileUtils


class TestLoggingControl:
    """Test suite for FileUtils logging control features."""

    def test_default_logging(self, temp_dir):
        """Test that default behavior remains unchanged (INFO level)."""
        fu = FileUtils(project_root=temp_dir)
        assert fu.logger.level == logging.INFO

    def test_quiet_mode(self, temp_dir):
        """Test that quiet mode sets CRITICAL level."""
        fu = FileUtils(project_root=temp_dir, quiet=True)
        assert fu.logger.level == logging.CRITICAL

    def test_explicit_log_level_int(self, temp_dir):
        """Test explicit log level using logging constant."""
        fu = FileUtils(project_root=temp_dir, log_level=logging.WARNING)
        assert fu.logger.level == logging.WARNING

    def test_explicit_log_level_string(self, temp_dir):
        """Test explicit log level using string (backward compatibility)."""
        fu = FileUtils(project_root=temp_dir, log_level="WARNING")
        assert fu.logger.level == logging.WARNING

    def test_quiet_overridden_by_log_level(self, temp_dir):
        """Test that log_level parameter overrides quiet parameter."""
        # log_level should take precedence over quiet
        fu = FileUtils(project_root=temp_dir, quiet=True, log_level=logging.DEBUG)
        assert fu.logger.level == logging.DEBUG

    def test_quiet_mode_suppresses_info_logging(self, temp_dir, caplog):
        """Test that quiet mode suppresses INFO level logging."""
        with caplog.at_level(logging.INFO):
            fu = FileUtils(project_root=temp_dir, quiet=True)

            # Even though we captured at INFO level, the logger should be at CRITICAL
            # So INFO messages should not be logged
            assert fu.logger.level == logging.CRITICAL

            # Try to log an INFO message
            fu.logger.info("This should not appear")

            # Verify that no INFO messages were actually logged
            info_records = [r for r in caplog.records if r.levelno == logging.INFO]
            assert len(info_records) == 0

    def test_json_output_clean(self, temp_dir):
        """Integration test: verify quiet mode produces clean stdout output."""

        import pandas as pd

        from FileUtils.core.enums import OutputFileType

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            # Create FileUtils in quiet mode
            fu = FileUtils(project_root=temp_dir, quiet=True)

            # Perform operations
            df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
            saved_files, _ = fu.save_data_to_storage(
                data=df,
                output_filetype=OutputFileType.JSON,
                output_type="processed",
                file_name="test_json",
                include_timestamp=False,
            )

            # Output should be clean (no logging)
            output = captured_output.getvalue()

            # In quiet mode, there should be no INFO logging output
            # (Though the test itself doesn't print JSON, in real usage
            # the application would print structured output here)
            assert "FileUtils initialized" not in output
            assert "Project root:" not in output
            assert "INFO" not in output

        finally:
            sys.stdout = old_stdout

    def test_debug_mode_verbose(self, temp_dir, caplog):
        """Test that DEBUG mode shows verbose logging."""
        with caplog.at_level(logging.DEBUG):
            fu = FileUtils(project_root=temp_dir, log_level=logging.DEBUG)

            assert fu.logger.level == logging.DEBUG

            # Log a debug message
            fu.logger.debug("Debug message")

            # Verify debug message was captured
            debug_records = [r for r in caplog.records if r.levelno == logging.DEBUG]
            assert len(debug_records) > 0

    def test_warning_level_filters_info(self, temp_dir, caplog):
        """Test that WARNING level filters out INFO messages."""
        with caplog.at_level(logging.DEBUG):  # Capture all levels
            fu = FileUtils(project_root=temp_dir, log_level=logging.WARNING)

            assert fu.logger.level == logging.WARNING

            # Try logging at different levels
            fu.logger.info("Info message")
            fu.logger.warning("Warning message")

            # Only WARNING and above should be logged
            info_records = [r for r in caplog.records if r.levelno == logging.INFO]
            warning_records = [
                r for r in caplog.records if r.levelno == logging.WARNING
            ]

            # INFO should be filtered out
            assert len(info_records) == 0
            # WARNING should be present
            assert len(warning_records) > 0

    def test_quiet_with_storage_type(self, temp_dir):
        """Test quiet mode works with storage_type parameter."""
        fu = FileUtils(project_root=temp_dir, storage_type="local", quiet=True)
        assert fu.logger.level == logging.CRITICAL

    def test_log_level_string_case_insensitive(self, temp_dir):
        """Test that string log levels are case-insensitive."""
        # Test lowercase
        fu1 = FileUtils(project_root=temp_dir, log_level="warning")
        assert fu1.logger.level == logging.WARNING

        # Test uppercase
        fu2 = FileUtils(project_root=temp_dir, log_level="WARNING")
        assert fu2.logger.level == logging.WARNING

        # Test mixed case
        fu3 = FileUtils(project_root=temp_dir, log_level="Warning")
        assert fu3.logger.level == logging.WARNING
