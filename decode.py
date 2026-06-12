import sys
import csv
import warnings

from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import textract
from array import array
from sys import byteorder as system_endian
from os import stat


# Separators used by the legacy (pair-based) decoder
_SEPARATORS = ["_", ")", ":", ";", ".", ",", " ", "\"", "'"]


def main():
    path = str(sys.argv[1])
    lines = textract.process(path).decode("utf-8", errors="ignore").lower().split("\n")

    if len(sys.argv) == 4 and str(sys.argv[3]) == "-b":
        fromBinary = read_file(str(sys.argv[2]), sys.byteorder)
        handle_binary(lines, fromBinary.tolist())
    else:
        with open(str(sys.argv[2])) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=",")
            for row in csvreader:
                handle(lines, row)


def read_file(filename, endian):
    count = stat(filename).st_size // 2
    with open(filename, "rb") as f:
        result = array("h")
        result.fromfile(f, count)
        if endian != system_endian:
            result.byteswap()
        return result


def handle(lines, row):
    n = len(row)

    if n % 3 == 0:
        # New format: triplets (line, char, length)
        _decode_triplets(lines, row)
    elif n % 2 == 0:
        # Legacy format: pairs (line, char) — separator-based decoding
        _decode_pairs_legacy(lines, row)
    else:
        print("Error: encoded row has an unexpected number of values ({})".format(n))
        sys.exit(1)


def handle_binary(lines, values):
    n = len(values)

    if n % 3 == 0:
        _decode_triplets(lines, values)
    elif n % 2 == 0:
        _decode_pairs_legacy(lines, values)
    else:
        print("Error: encoded binary data has an unexpected number of values ({})".format(n))
        sys.exit(1)


def _decode_triplets(lines, row):
    """Decode triplet format: (line, char, length) — exact length extraction."""
    words = ""
    wordTotal = len(row) // 3
    for idx in range(wordTotal):
        lineNr = int(row[idx * 3])
        charNr = int(row[idx * 3 + 1])
        length = int(row[idx * 3 + 2])
        words += lines[lineNr][charNr : charNr + length]
    print(words)


def _decode_pairs_legacy(lines, row):
    """Decode legacy pair format: (line, char) — read until a separator."""
    words = ""
    wordTotal = len(row) // 2
    for idx in range(wordTotal):
        lineNr = int(row[idx * 2])
        charNr = int(row[idx * 2 + 1])
        subline = lines[lineNr][charNr:]

        # Find the nearest separator character
        sepIdx = -1
        for seperator in _SEPARATORS:
            i = subline.find(seperator)
            if i != -1 and (sepIdx == -1 or i < sepIdx):
                sepIdx = i
        if sepIdx == -1:
            sepIdx = len(subline)

        words += subline[:sepIdx] + " "
    print(words)


if __name__ == "__main__":
    main()
