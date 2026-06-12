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
    def test_encodes_words_to_triplets(self, key_file, input_csv_file, work_dir):
        """Encoding 'secret message' should produce line,char,len triplets."""
        _run_encode(key_file, input_csv_file)
        indices = _read_csv("out.csv")
        # tokenize("secret message") → ["secret", " ", "message"]
        # "secret"  → line 1, char 10, len 6
        # " "       → line 0, char  3, len 1
        # "message" → line 1, char 17, len 7
        assert indices == [1, 10, 6, 0, 3, 1, 1, 17, 7]

    def test_encodes_multiple_words(self, key_file, work_dir):
        """Encoding 'the quick brown fox' should produce correct triplets."""
        csv_path = os.path.join(work_dir, "input.csv")
        with open(csv_path, "w") as f:
            f.write("the quick brown fox\n")
        _run_encode(key_file, csv_path)
        indices = _read_csv("out.csv")
        # tokenize("the quick brown fox") → ["the"," ","quick"," ","brown"," ","fox"]
        # "the"   → line 0, char  0, len 3
        # " "     → line 0, char  3, len 1
        # "quick" → line 0, char  4, len 5
        # " "     → line 0, char  3, len 1
        # "brown" → line 0, char 10, len 5
        # " "     → line 0, char  3, len 1
        # "fox"   → line 0, char 16, len 3
        assert indices == [
            0, 0, 3,
            0, 3, 1,
            0, 4, 5,
            0, 3, 1,
            0, 10, 5,
            0, 3, 1,
            0, 16, 3,
        ]

    def test_character_not_found_exits_with_error(self, key_file, work_dir, capsys):
        """Encoding a char not in the key document should print error and exit."""
        csv_path = os.path.join(work_dir, "input.csv")
        with open(csv_path, "w") as f:
            f.write("hello123\n")
        with pytest.raises(SystemExit):
            _run_encode(key_file, csv_path)
        captured = capsys.readouterr()
        assert "does not contain value" in captured.out

    def test_unknown_word_is_split_into_subwords(self, key_file, work_dir):
        """A word not in the key doc should be split into known subword pieces."""
        csv_path = os.path.join(work_dir, "input.csv")
        with open(csv_path, "w") as f:
            f.write("obfusee\n")
        _run_encode(key_file, csv_path)
        indices = _read_csv("out.csv")
        # "obfusee" tokenizes (on this small doc, with 500 vocab, with
        # default merges) into pieces like ["o","b","f","u","se","e"].
        # Each piece is a triplet.
        assert len(indices) % 3 == 0
        assert len(indices) >= 3  # at least one token


class TestEncodeBinary:
    def test_encodes_to_pcm_binary(self, key_file, input_csv_file, work_dir):
        """Binary mode should produce a .pcm file with matching triplets."""
        _run_encode(key_file, input_csv_file, binary=True)
        indices = _read_pcm("out.pcm")
        assert indices == [1, 10, 6, 0, 3, 1, 1, 17, 7]

    def test_binary_and_csv_produce_same_data(self, key_file, input_csv_file, work_dir):
        """Binary and CSV modes should encode the same indices."""
        _run_encode(key_file, input_csv_file, binary=True)
        _run_encode(key_file, input_csv_file, binary=False)
        csv_indices = _read_csv("out.csv")
        pcm_indices = _read_pcm("out.pcm")
        assert csv_indices == pcm_indices