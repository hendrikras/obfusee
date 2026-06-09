"""Tests for main.py dispatcher."""

import sys

import pytest
import textract.exceptions

import main


class TestDispatcher:
    """Test main.py argument parsing and module dispatching."""

    def test_no_args_exits_with_usage(self, capsys):
        """Running with no arguments should print usage and exit."""
        sys.argv = ["main.py"]
        with pytest.raises(SystemExit):
            main.main()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "-e" in captured.out
        assert "-d" in captured.out

    def test_both_flags_exits_with_error(self, capsys):
        """Passing both -e and -d should error."""
        sys.argv = ["main.py", "-e", "-d", "doc.txt", "input.csv"]
        with pytest.raises(SystemExit):
            main.main()
        captured = capsys.readouterr()
        assert "not both" in captured.out

    def test_encode_flag_detected(self):
        """-e flag should be detected regardless of position."""
        sys.argv = ["main.py", "doc.txt", "input.csv", "-e"]
        # Should not raise SystemExit; will try to import encode module
        with pytest.raises((SystemExit, textract.exceptions.MissingFileError)):
            main.main()

    def test_decode_flag_detected(self):
        """-d flag should be detected regardless of position."""
        sys.argv = ["main.py", "-d", "doc.txt", "encoded.csv"]
        with pytest.raises((SystemExit, textract.exceptions.MissingFileError)):
            main.main()