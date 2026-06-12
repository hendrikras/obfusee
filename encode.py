import sys
import csv
import warnings

from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import textract
import array

from tokenizer import BPETokenizer


def main():
    path = str(sys.argv[1])
    doc_text = textract.process(path).decode("utf-8", errors="ignore").lower()
    lines = doc_text.split("\n")

    # Train BPE tokenizer on the key document
    tokenizer = BPETokenizer(vocab_size=500)
    tokenizer.train(doc_text)

    outArray = []

    with open(str(sys.argv[2])) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=" ")
        for row in csvReader:
            # Reconstruct the full message with spaces
            message = " ".join(row)
            tokens = tokenizer.tokenize(message)
            for token in tokens:
                found = False
                for idx, val in enumerate(lines):
                    pos = val.find(token)
                    if pos != -1:
                        outArray.append(idx)             # line number
                        outArray.append(pos)             # character position
                        outArray.append(len(token))      # token length
                        found = True
                        break
                if not found:
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
