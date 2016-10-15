

import sys 

maximal = False 

def getMaximal(freqSeq):
	maxLength = 0
	for i in traces.keys():
		if maxLength < len(freqSeq[i]):
			maxLength = len(freqSeq[i])
	k = maxLength
	toBeRemoved = []
	while k > 1:
		for i in freqSeq.keys():
			if len(freqSeq[i]) == k:
				for j in freqSeq.keys():
					if j != i:
						if contains_sublist(freqSeq[i], freqSeq[j]):
							toBeRemoved.append(j)
		if len(toBeRemoved) != 0:
			for t in toBeRemoved:
				del freqSeq[t]
				toBeRemoved = []					 
		k-=1
	return freqSeq
	
def contains_sublist(lst, sublst):
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in range(len(lst)-n+1))
    
    	     
if len(sys.argv) < 2:
	print("This program needs a log.txt file as parameter")
	exit()
else:
	filename = sys.argv[1]
if len(sys.argv) == 3:
	if sys.argv[2] == "-max":
		maximal = True

try:
	log = open(filename, encoding='utf-8')
	log.readline() # firstline is useless
	traces = dict()
	traces[1] = log.readline().strip().split()
	traces[1] = traces[1][3:]
	for i in range (len(traces[1])):
		traces[1][i] = traces[1][i].strip('<>')
	
	line = log.readline().strip()
	j = 2
	while line!="":
		traces[j] = line.split()
		traces[j] = traces[j][1:]
		for e in range (len(traces[j])):
			traces[j][e] = traces[j][e].strip('<>')
		j+=1
		line = log.readline().strip()
	print(traces)
	if maximal == True:
		traces = getMaximal(traces)
		print("After pruning non-maximal sequences: ")	
		print(traces)
except IOError:
	print ("Error: can\'t find file or read content!")
else:
	print ("Opened and read the file successfully")
	log.close()
	
	
try:
	promInput = open(filename+'.txt','wt',encoding='utf-8')
	promInput.write('traceID;eventID \n')
	traceID = 0
	for i in traces.keys():
		for j in range(len(traces[i])):
			promInput.write('t'+str(traceID)+';'+traces[i][j]+'\n')
		traceID += 1
except IOError:
	print ("Error: can\'t create or write in output file!")
else:
	print ("Created and written in the file successfully")
	promInput.close()
