"""Tests for the decode module."""

import sys
import tempfile
import os
import io
from contextlib import redirect_stdout

import pytest

import decode


class TestHandle:
    """Test decode.handle() directly — it's the core decoding logic."""

    def test_decodes_single_word(self, key_text):
        """Decoding a single line,char pair should return that word."""
        lines = key_text.split("\n")
        row = ["0", "0"]  # line 0, char 0 → "the"
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "the"

    def test_decodes_multiple_words(self, key_text):
        """Decoding multiple pairs should reconstruct the phrase."""
        lines = key_text.split("\n")
        row = ["0", "0", "0", "4", "0", "10", "0", "16"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "the quick brown fox"

    def test_decodes_from_different_lines(self, key_text):
        """Words can span different lines in the key document."""
        lines = key_text.split("\n")
        # "fox" (0,16), "secret" (1,10), "message" (1,17), "world" (2,6)
        row = ["0", "16", "1", "10", "1", "17", "2", "6"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "fox secret message world"

    def test_stops_at_separator(self):
        """Decoding should stop at punctuation/whitespace separators."""
        lines = ["hello, world! this:test;"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, ["0", "0"])
        assert buf.getvalue().strip() == "hello"

    def test_reads_to_end_of_line_when_no_separator(self):
        """If no separator found, decode should read to end of line."""
        lines = ["nopunctuationhere"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, ["0", "0"])
        assert buf.getvalue().strip() == "nopunctuationhere"


class TestDecodeCSV:
    """Integration tests for decode.main() with CSV input."""

    def _run_decode_csv(self, key_path, encoded_path):
        old_argv = sys.argv
        sys.argv = ["decode.py", key_path, encoded_path]
        try:
            decode.main()
        finally:
            sys.argv = old_argv

    def test_decodes_csv_to_message(self, key_file, encoded_csv_file, capsys):
        """Decoding a CSV should print the reconstructed message."""
        self._run_decode_csv(key_file, encoded_csv_file)
        captured = capsys.readouterr()
        assert captured.out.strip() == "secret message"


class TestDecodeBinary:
    """Integration tests for decode.main() with binary PCM input."""

    def _run_decode_binary(self, key_path, pcm_path):
        old_argv = sys.argv
        sys.argv = ["decode.py", key_path, pcm_path, "-b"]
        try:
            decode.main()
        finally:
            sys.argv = old_argv

    def test_decodes_pcm_to_message(self, key_file, capsys):
        """Decoding a PCM binary should print the reconstructed message."""
        import array
        pcm_data = array.array("h", [1, 10, 1, 17])
        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as f:
            pcm_data.tofile(f)
            pcm_path = f.name
        try:
            self._run_decode_binary(key_file, pcm_path)
            captured = capsys.readouterr()
            assert captured.out.strip() == "secret message"
        finally:
            os.unlink(pcm_path)