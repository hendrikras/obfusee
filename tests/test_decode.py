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
        """Decoding a single triplet should return that word."""
        lines = key_text.split("\n")
        row = ["0", "0", "3"]  # line 0, char 0, len 3 → "the"
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "the"

    def test_decodes_multiple_words_with_spaces(self, key_text):
        """Decoding triplets including space tokens should reconstruct the phrase."""
        lines = key_text.split("\n")
        # "the quick brown fox" → tokens: ["the"," ","quick"," ","brown"," ","fox"]
        row = [
            "0", "0", "3",     # "the"
            "0", "3", "1",     # " "
            "0", "4", "5",     # "quick"
            "0", "3", "1",     # " "
            "0", "10", "5",    # "brown"
            "0", "3", "1",     # " "
            "0", "16", "3",    # "fox"
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "the quick brown fox"

    def test_decodes_from_different_lines(self, key_text):
        """Tokens can span different lines in the key document."""
        lines = key_text.split("\n")
        # "fox secret message world"
        # tokens: ["fox"," ","secret"," ","message"," ","world"]
        row = [
            "0", "16", "3",    # "fox"    → line 0
            "0", "3", "1",     # " "
            "1", "10", "6",    # "secret" → line 1
            "0", "3", "1",     # " "
            "1", "17", "7",    # "message"→ line 1
            "0", "3", "1",     # " "
            "2", "6", "5",     # "world"  → line 2
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, row)
        assert buf.getvalue().strip() == "fox secret message world"

    def test_exact_length_extraction(self):
        """Decoder uses the length field, not separator-based parsing."""
        lines = ["hello, world! this:test;"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, ["0", "0", "5"])
        assert buf.getvalue().strip() == "hello"

    def test_reads_partial_token_by_length(self):
        """Decoder should read exactly `length` chars, even if a separator is inside."""
        lines = ["abc,def"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, ["0", "0", "4"])
        assert buf.getvalue().strip() == "abc,"

    def test_reads_beyond_separator_by_length(self):
        """Decoder reads exact length regardless of separators."""
        lines = ["abc,def"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            decode.handle(lines, ["0", "0", "7"])
        assert buf.getvalue().strip() == "abc,def"


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
        # triplets: "secret" (1,10,6), " " (0,3,1), "message" (1,17,7)
        pcm_data = array.array("h", [1, 10, 6, 0, 3, 1, 1, 17, 7])
        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as f:
            pcm_data.tofile(f)
            pcm_path = f.name
        try:
            self._run_decode_binary(key_file, pcm_path)
            captured = capsys.readouterr()
            assert captured.out.strip() == "secret message"
        finally:
            os.unlink(pcm_path)