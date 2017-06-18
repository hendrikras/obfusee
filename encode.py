import sys
import csv
import textract

path =  str(sys.argv[1])
lines = textract.process(path).lower()
inArray = lines.split("\n")
outArray = []
with open(str(sys.argv[2])) as csvfile:
	csvReader = csv.reader(csvfile, delimiter=" ")
	for row in csvReader:
		for inputstr in row:
			for idx, val in enumerate(inArray):
				if inputstr in val:
					checkIdx = val.find(inputstr)
					lastIdx = checkIdx + len(inputstr)
					if len(val) <= lastIdx:
						lastchar = " "
					else:
						lastchar = val[lastIdx]
					sepList = [ "_", ")", ":", ";", ".", ",", " ", "\"", "'"]
					if any (lastchar in s for s in sepList):
						outArray.append(str(idx) +","+ str(val.find(inputstr)))
						break
				elif idx+1 == len(inArray):
					print "the cipher key (document) does not contain value: " + inputstr
					quit()

with open("out.csv", "a") as csvfile:
	writer = csv.writer(csvfile, lineterminator="\n")
	writer.writerow(outArray)
