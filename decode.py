import sys
import csv
import textract
import struct
from array import array
# Edit:
from sys import byteorder as system_endian # thanks, Sven!
# Sigh...
from os import stat

path =  str(sys.argv[1])
lines = textract.process(path).lower().split("\n")

def read_file(filename, endian):
	count = stat(filename).st_size / 2
	with file(filename, 'rb') as f:
		result = array('h')
		result.fromfile(f, count)
		if endian != system_endian: result.byteswap()
		return result

def handle(row):
	words = ""
	wordTotal = len(row) / 2
	for idx in range(0, wordTotal):
		lineNr = int(row[idx*2])
		charNr = int(row[(idx*2)+1])
		seperatorIdx = -1
		subline = lines[lineNr][charNr:]
		sepList = [ "_", ")", ":", ";", ".", ",", " ", "\"", "'"]
		for seperator in sepList:
			idx = subline.find(seperator)
			if idx != -1:
				if seperatorIdx == -1 or (seperatorIdx != -1 and idx < seperatorIdx):
					seperatorIdx = idx
			if seperatorIdx == -1:
				seperatorIdx = len(lines[lineNr])
		words += subline[:seperatorIdx]+" "
	print words

if len(sys.argv) == 4 and str(sys.argv[3]) == '-b':
	fromBinary = read_file('out.pcm', sys.byteorder)
	handle(fromBinary.tolist())
else:
	with open(str(sys.argv[2])) as csvfile:
		csvreader = csv.reader(csvfile, delimiter= ',')
		for row in csvreader:
			handle(row)
