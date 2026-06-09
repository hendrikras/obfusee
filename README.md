# obfusee
A very simple book cipher encoder/ decoder for the command line

It will take an input file written in plain text, and will try to find the individual words in a key file.
This can include: txt, pdf, epub, word or any other format supported by textract.

The key file needs to have all words mentioned that are also listed in the input file,
or it will exit mentioning the word it can't find.
If successful, a csv or binary output file is created with the references to lines and words from the key file.
The original key file can then be used to decode the message.

Python and the textract package is required to run. This project uses [uv](https://docs.astral.sh/uv/) for package management.

```
uv sync
```

> **Note:** textract has system-level dependencies (antiword, poppler, etc.).
> See the [textract installation guide](http://textract.readthedocs.io/en/stable/installation.html) if you run into issues.

## Usage

All operations go through `main.py` with a mode flag:

```
uv run python main.py -e <key_document> <input_csv> [-b]    # encode
uv run python main.py -d <key_document> <encoded_file> [-b]  # decode
```

The flag can appear anywhere in the argument list; all other arguments are forwarded
to the appropriate sub-module.

### Examples

Encode a message:

```
uv run python main.py -e example_key_doc.epub input.csv
```

Decode the result:

```
uv run python main.py -d example_key_doc.epub out.csv
```

### Binary mode

Add `-b` to use a binary PCM output/input file instead of CSV.
This makes the output smaller and harder to eyeball with a text editor:

```
uv run python main.py -e example_key_doc.epub input.csv -b
uv run python main.py -d example_key_doc.epub out.pcm -b
```

> **Note:** The individual `encode.py` and `decode.py` scripts can still be called directly
> if you prefer to bypass the dispatcher.

## Standalone binary

You can freeze the project into a single executable with PyInstaller — no Python
runtime needed on the target machine.

```
uv run pyinstaller --onefile --name obfusee \
  --hidden-import encode --hidden-import decode \
  --collect-all textract main.py
```

The binary is placed at `dist/obfusee` (~56 MB on macOS arm64).

```
./dist/obfusee -e example_key_doc.epub input.csv
./dist/obfusee -d example_key_doc.epub out.csv
./dist/obfusee -e example_key_doc.epub input.csv -b
./dist/obfusee -d example_key_doc.epub out.pcm -b
```

## Testing

Unit tests cover encoding, decoding, the main dispatcher, and end-to-end roundtrips.

```
.venv/bin/python -m pytest tests/ -v
```
