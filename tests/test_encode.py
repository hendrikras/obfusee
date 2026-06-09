"""Tests for the encode module."""

import sys
import csv
import array
import os

import pytest

import encode


def _run_encode(key_path, input_path, binary=False):
    """Helper: run encode.main() with controlled sys.argv."""
    old_argv = sys.argv
    args = [key_path, input_path]
    if binary:
        args.append("-b")
    sys.argv = ["encode.py"] + args
    try:
        encode.main()
    finally:
        sys.argv = old_argv


def _read_csv(path):
    """Read a CSV output file and return the first row as a list of ints."""
    with open(path) as f:
        reader = csv.reader(f, delimiter=",")
        return [int(x) for x in next(reader)]


def _read_pcm(path):
    """Read a PCM binary output file and return a list of 16-bit ints."""
    result = array.array("h")
    with open(path, "rb") as f:
        result.fromfile(f, (os.path.getsize(path) // 2))
    return result.tolist()


class TestEncodeCSV:
    def test_encodes_words_to_line_char_indices(self, key_file, input_csv_file, work_dir):
        """Encoding 'secret message' should produce correct line,char pairs."""
        _run_encode(key_file, input_csv_file)
        indices = _read_csv("out.csv")
        # "secret" → line 1, char 10; "message" → line 1, char 17
        assert indices == [1, 10, 1, 17]

    def test_encodes_multiple_words(self, key_file, work_dir):
        """Encoding 'the quick brown fox' should produce correct indices."""
        csv_path = os.path.join(work_dir, "input.csv")
        with open(csv_path, "w") as f:
            f.write("the quick brown fox\n")
        _run_encode(key_file, csv_path)
        indices = _read_csv("out.csv")
        # "the" → line 0, char 0; "quick" → line 0, char 4
        # "brown" → line 0, char 10; "fox" → line 0, char 16
        assert indices == [0, 0, 0, 4, 0, 10, 0, 16]

    def test_word_not_found_exits_with_error(self, key_file, work_dir, capsys):
        """Encoding a word not in the key document should print error and exit."""
        csv_path = os.path.join(work_dir, "input.csv")
        with open(csv_path, "w") as f:
            f.write("nonexistentword\n")
        with pytest.raises(SystemExit):
            _run_encode(key_file, csv_path)
        captured = capsys.readouterr()
        assert "does not contain value" in captured.out


class TestEncodeBinary:
    def test_encodes_to_pcm_binary(self, key_file, input_csv_file, work_dir):
        """Binary mode should produce a .pcm file with matching indices."""
        _run_encode(key_file, input_csv_file, binary=True)
        indices = _read_pcm("out.pcm")
        assert indices == [1, 10, 1, 17]

    def test_binary_and_csv_produce_same_data(self, key_file, input_csv_file, work_dir):
        """Binary and CSV modes should encode the same indices."""
        _run_encode(key_file, input_csv_file, binary=True)
        _run_encode(key_file, input_csv_file, binary=False)
        csv_indices = _read_csv("out.csv")
        pcm_indices = _read_pcm("out.pcm")
        assert csv_indices == pcm_indices