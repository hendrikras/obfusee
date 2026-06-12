# obfusee

A book cipher encoder/decoder with **BPE subword tokenization** — like LLMs do.

It takes a plain-text message and encodes it as (line, character, length) triplets
pointing into a key document (txt, pdf, epub, etc.). The same document is used to
decode the original message.

Because the encoder uses **BPE (Byte Pair Encoding)** to split words into subword
tokens, any word can be encoded — even words that don't appear verbatim in the key
document. For example, "obfusee" and "xyzzysomething" work fine as long as their
subword pieces (characters and frequent n-grams) exist in the document.

## Setup

Python 3 and the textract package are required. This project uses
[uv](https://docs.astral.sh/uv/) for package management.

```
uv sync
```

> **Note:** textract has system-level dependencies (antiword, poppler, etc.).
> See the [textract installation guide](http://textract.readthedocs.io/en/stable/installation.html)
> if you run into issues.

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

### Subword tokenization

The encoder uses a **hybrid approach** for maximum compatibility:

1. **Whole-word match** (preferred) — if the word appears as a substring in the
   key document, it is encoded as a single token. This matches the behaviour of
   earlier versions for words that exist in the document.
2. **BPE subword fallback** — if the word is not found, a BPE tokenizer (trained
   on the key document with 500 merges) splits it into known subword pieces.
   These pieces are guaranteed to exist in the document since they are derived
   from it.

This means:

- Words that exist in the document are encoded as single tokens (backwards
  compatible).
- Words that **don't** exist in the document are split into smaller pieces
  (down to individual characters if needed).

Each token is stored as a triplet — `(line, character_position, length)` — that
points to its occurrence in the key document. The decoder reads exactly `length`
characters from that position, so no separator-based scanning is needed.

> **Note:** The individual `encode.py` and `decode.py` scripts can still be called
> directly if you prefer to bypass the dispatcher.

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