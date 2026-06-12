import sys
import csv
import warnings

from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import textract
import array

from tokenizer import BPETokenizer


def _find(lines, token):
    """Search for *token* as a substring in *lines*.

    Returns (line_index, char_position) or None.
    """
    for idx, val in enumerate(lines):
        pos = val.find(token)
        if pos != -1:
            return idx, pos
    return None


def main():
    path = str(sys.argv[1])
    doc_text = textract.process(path).decode("utf-8", errors="ignore").lower()
    lines = doc_text.split("\n")

    # Train BPE tokenizer on the key document (used as fallback)
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(doc_text)

    outArray = []

    with open(str(sys.argv[2])) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=" ")
        for row in csvReader:
            for word_idx, inputword in enumerate(row):
                # Insert a space token between words
                if word_idx > 0:
                    loc = _find(lines, " ")
                    if loc is None:
                        print("the cipher key (document) does not contain a space")
                        quit()
                    outArray.append(loc[0])        # line number
                    outArray.append(loc[1])        # character position
                    outArray.append(1)             # token length

                # 1) Try whole-word match first (backwards compatible)
                loc = _find(lines, inputword)
                if loc is not None:
                    outArray.append(loc[0])
                    outArray.append(loc[1])
                    outArray.append(len(inputword))
                    continue

                # 2) Fall back to BPE subword tokenization
                tokens = tokenizer.tokenize(inputword)
                for token in tokens:
                    loc = _find(lines, token)
                    if loc is not None:
                        outArray.append(loc[0])
                        outArray.append(loc[1])
                        outArray.append(len(token))
                    else:
                        print(
                            "the cipher key (document) does not contain value: "
                            + repr(token)
                        )
                        quit()

    if len(sys.argv) == 4 and str(sys.argv[3]) == "-b":
        with open("out.pcm", "wb") as out:
            pcm_vals = array.array("h", outArray)  # 16-bit signed
            pcm_vals.tofile(out)
    else:
        with open("out.csv", "w") as csvfile:
            writer = csv.writer(csvfile, lineterminator="\n")
            writer.writerow(outArray)


if __name__ == "__main__":
    main()