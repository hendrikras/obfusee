import sys
import csv
import textract

path =  str(sys.argv[1])
lines = textract.process(path).lower().split("\n")

with open(str(sys.argv[2])) as csvfile:
	csvreader = csv.reader(csvfile, delimiter= ',', quotechar='"')
	for row in csvreader:
		words = ""
		for item in row:
			lineNr = int(item.split(',')[0])
			charNr = int(item.split(',')[1])
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
