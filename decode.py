import sys
import csv
import warnings

from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import textract
from array import array
from sys import byteorder as system_endian
from os import stat


def main():
	path = str(sys.argv[1])
	lines = textract.process(path).decode('utf-8', errors='ignore').lower().split("\n")

	if len(sys.argv) == 4 and str(sys.argv[3]) == '-b':
		fromBinary = read_file(str(sys.argv[2]), sys.byteorder)
		handle(lines, fromBinary.tolist())
	else:
		with open(str(sys.argv[2])) as csvfile:
			csvreader = csv.reader(csvfile, delimiter=',')
			for row in csvreader:
				handle(lines, row)


def read_file(filename, endian):
	count = stat(filename).st_size // 2
	with open(filename, 'rb') as f:
		result = array('h')
		result.fromfile(f, count)
		if endian != system_endian:
			result.byteswap()
		return result

def handle(lines, row):
	words = ""
	wordTotal = len(row) // 2
	for idx in range(0, wordTotal):
		lineNr = int(row[idx*2])
		charNr = int(row[(idx*2)+1])
		seperatorIdx = -1
		subline = lines[lineNr][charNr:]
		sepList = [ "_", ")", ":", ";", ".", ",", " ", "\"", "'"]
		for seperator in sepList:
			i = subline.find(seperator)
			if i != -1:
				if seperatorIdx == -1 or (seperatorIdx != -1 and i < seperatorIdx):
					seperatorIdx = i
			if seperatorIdx == -1:
				seperatorIdx = len(lines[lineNr])
		words += subline[:seperatorIdx] + " "
	print(words)

if __name__ == "__main__":
	main()