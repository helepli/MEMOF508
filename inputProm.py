
import sys 

maximal = False 
closed = False
subString = False

def getMaximal(freqSeq):
	maxLength = 0
	for i in traces.keys():
		if maxLength < len(freqSeq[i]):
			maxLength = len(freqSeq[i])
	k = maxLength
	toBeRemoved = set()
	while k > 1:
		for i in freqSeq.keys():
			if len(freqSeq[i]) == k:
				for j in freqSeq.keys():
					if j != i and isSubseq(freqSeq[i], freqSeq[j]):
						toBeRemoved.add(j)
		if len(toBeRemoved) != 0:
			for t in toBeRemoved:
				del freqSeq[t]
				toBeRemoved = set()					 
		k-=1
	return freqSeq
	
	
def getClosed(freqSeq):
	toBeRemoved = set()
	for i in freqSeq.keys(): 
		for j in freqSeq.keys():
			if len(freqSeq[i]) < len(freqSeq[j]) and isSubseq(freqSeq[j], freqSeq[i]):
				if supports[i-1] == supports[j-1]:
					toBeRemoved.add(i)
	if len(toBeRemoved) != 0:
		for t in toBeRemoved:
			del freqSeq[t]	
			
	return freqSeq

def isSubseq(lst, sublst):
	if subString:
		return containsSubstring(lst, sublst)
	else:
		return containsSubseq(lst, sublst)
	
def containsSubseq(lst, sublst):
	result = []
	j = 0
	for item in lst:
		if item == sublst[j]:
			result.append(item)
			j += 1
			if j == len(sublst):
				break
	return (result == sublst)


def containsSubstring(lst, sublst):
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in range(len(lst)-n+1))
    
    
    	     
if len(sys.argv) < 2:
	print("This program needs a log.txt file as parameter")
	exit()
else:
	filename = sys.argv[1]
if len(sys.argv) >= 3:
	maximal = sys.argv[2] == "-max"
	closed = sys.argv[2] == "-clo"
	if len(sys.argv) == 4:
		subString = sys.argv[3] == "-str"

try:
	log = open(filename, encoding='utf-8')
	log.readline() # firstline is useless
	traces = dict()
	traces[1] = log.readline().strip().split()
	if closed == True:
		supports = []
		supports.append(float(traces[1][2].strip(':')))
	traces[1] = traces[1][3:]
	for i in range (len(traces[1])):
		traces[1][i] = traces[1][i].strip('<>')
	
	line = log.readline().strip()
	j = 2
	while line!="":
		traces[j] = line.split()
		if closed:
			supports.append(float(traces[j][0].strip(':')))
		traces[j] = traces[j][1:]
		for e in range (len(traces[j])):
			traces[j][e] = traces[j][e].strip('<>')
		j+=1
		line = log.readline().strip()
	print(traces)
	
	if maximal:
		traces = getMaximal(traces)
		print("After pruning non-maximal sequences: ") 			
		print(traces)
	elif closed:
		print("Supports: ")
		print(supports)
		traces = getClosed(traces)
		print("After pruning non-closed sequences: ")
		print(traces)
	
except IOError:
	print ("Error: can\'t find file or read content!")
	exit()
else:
	print ("Opened and read the file successfully")
	log.close()
	
	
try:
	smth = ""
	if maximal:
		smth = "_max"
	elif closed:
		smth = "_closed"
	if subString:
		smth+="_subStr"

	outName = "log" + smth + filename.strip('.rqes') + ".txt"
	promInput = open(outName,'wt',encoding='utf-8')
	promInput.write('traceID;eventID \n')
	traceID = 0
	for i in traces.keys():
		for j in range(len(traces[i])):
			promInput.write('t'+str(traceID)+';'+traces[i][j]+'\n')
		traceID += 1
except IOError:
	print ("Error: can\'t create or write in output file!")
	exit()
else:
	print ("Created and written in the file successfully")
	promInput.close()
