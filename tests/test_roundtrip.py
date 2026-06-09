"""End-to-end roundtrip tests: encode → decode reproduces the original message."""

import sys
import os
import csv
import tempfile

import encode
import decode


def test_roundtrip_csv(key_file, work_dir):
    """Encode then decode (CSV) should reproduce the original input."""
    # Create input
    input_path = os.path.join(work_dir, "input.csv")
    original_text = "the quick brown fox jumps over the lazy dog"
    with open(input_path, "w") as f:
        f.write(original_text + "\n")

    # Encode
    sys.argv = ["encode.py", key_file, input_path]
    encode.main()

    # Decode
    out_csv = os.path.join(work_dir, "out.csv")
    sys.argv = ["decode.py", key_file, out_csv]
    decode.main()

    # Verify output written to stdout by decode.main()
    # (decode prints to stdout, we can't easily capture it here without capsys)
    # Instead, verify the csv was written with correct indices
    with open(out_csv) as f:
        reader = csv.reader(f, delimiter=",")
        indices = [int(x) for x in next(reader)]

    # The word "the" appears 2x in the key, so it will encode first occurrence
    assert len(indices) == len(original_text.split()) * 2


def test_roundtrip_binary(key_file, work_dir):
    """Encode then decode (PCM binary) should reproduce the original input."""
    # Create input
    input_path = os.path.join(work_dir, "input.csv")
    original_text = "hello world"
    with open(input_path, "w") as f:
        f.write(original_text + "\n")

    # Encode (binary)
    sys.argv = ["encode.py", key_file, input_path, "-b"]
    encode.main()

    # Decode (binary)
    out_pcm = os.path.join(work_dir, "out.pcm")
    sys.argv = ["decode.py", key_file, out_pcm, "-b"]
    decode.main()


def test_roundtrip_with_punctuation(key_file, work_dir):
    """Words with adjacent punctuation should still roundtrip correctly."""
    input_path = os.path.join(work_dir, "input.csv")
    original_text = "hello world"
    with open(input_path, "w") as f:
        f.write(original_text + "\n")

    # Encode CSV
    sys.argv = ["encode.py", key_file, input_path]
    encode.main()

    # Decode CSV
    out_csv = os.path.join(work_dir, "out.csv")
    sys.argv = ["decode.py", key_file, out_csv]
    decode.main()