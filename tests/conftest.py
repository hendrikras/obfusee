import tempfile
import os
import pytest


@pytest.fixture
def key_text():
    """Return the content of a small key document."""
    return (
        "the quick brown fox jumps over the lazy dog\n"
        "this is a secret message for testing\n"
        "hello world and all who inhabit it\n"
    )


@pytest.fixture
def key_file(key_text):
    """Create a temporary text file to use as a key document."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(key_text)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def input_csv_content():
    """Content of a simple CSV file with words to encode."""
    return "secret message\n"


@pytest.fixture
def input_csv_file(input_csv_content):
    """Create a temporary CSV input file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(input_csv_content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def encoded_csv_content():
    """Known encoded output: triplets into key_text above.

    key_text lines:
      0: "the quick brown fox jumps over the lazy dog"
      1: "this is a secret message for testing"
      2: "hello world and all who inhabit it"

    tokenize("secret message") → ["secret", " ", "message"]
    "secret"  → line 1, char 10, len 6
    " "       → line 0, char  3, len 1
    "message" → line 1, char 17, len 7
    """
    return "1,10,6,0,3,1,1,17,7\n"


@pytest.fixture
def encoded_csv_file(encoded_csv_content):
    """Create a temporary encoded CSV file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(encoded_csv_content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def work_dir():
    """Change to a temporary working directory so out.csv/out.pcm land there."""
    old_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        yield tmp
    os.chdir(old_cwd)