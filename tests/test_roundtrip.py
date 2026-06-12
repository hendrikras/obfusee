"""End-to-end roundtrip tests: encode → decode reproduces the original message."""

import sys
import os
import csv
import io
from contextlib import redirect_stdout

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

    # Decode — capture stdout
    out_csv = os.path.join(work_dir, "out.csv")
    sys.argv = ["decode.py", key_file, out_csv]
    buf = io.StringIO()
    with redirect_stdout(buf):
        decode.main()
    decoded = buf.getvalue().strip()

    assert decoded == original_text


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

    # Decode (binary) — capture stdout
    out_pcm = os.path.join(work_dir, "out.pcm")
    sys.argv = ["decode.py", key_file, out_pcm, "-b"]
    buf = io.StringIO()
    with redirect_stdout(buf):
        decode.main()
    decoded = buf.getvalue().strip()

    assert decoded == original_text


def test_roundtrip_uses_subword_tokenization(key_file, work_dir):
    """Words not in the key document should still roundtrip via subword splits."""
    input_path = os.path.join(work_dir, "input.csv")
    original_text = "obfusee works fine"
    with open(input_path, "w") as f:
        f.write(original_text + "\n")

    # Encode CSV
    sys.argv = ["encode.py", key_file, input_path]
    encode.main()

    # Decode CSV
    out_csv = os.path.join(work_dir, "out.csv")
    sys.argv = ["decode.py", key_file, out_csv]
    buf = io.StringIO()
    with redirect_stdout(buf):
        decode.main()
    decoded = buf.getvalue().strip()

    assert decoded == original_text