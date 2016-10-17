
import sys 

maximal = False 
closed = False

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
					if j != i and containsSubseq(freqSeq[i], freqSeq[j]):
						toBeRemoved.append(j)
		if len(toBeRemoved) != 0:
			for t in toBeRemoved:
				del freqSeq[t]
				toBeRemoved = []					 
		k-=1
	return freqSeq
	
	
def getClosed(freqSeq):
	toBeRemoved = set()
	for i in freqSeq.keys(): 
		print(i)
		for j in freqSeq.keys():
			if len(freqSeq[i]) < len(freqSeq[j]) and containsSubseq(freqSeq[j], freqSeq[i]):
				print("yeaaaaah")
				if supports[i-1] == supports[j-1]:
					print(freqSeq[i])
					print(freqSeq[j])
					toBeRemoved.add(i)
	if len(toBeRemoved) != 0:
		for t in toBeRemoved:
			del freqSeq[t]	
	
	return freqSeq
	
def containsSubseq(lst, sublst):
	print(lst)
	print(sublst)
	result = []
	j = 0
	for item in lst:
		print(j)
		if item == sublst[j]:
			print(item)
			result.append(item)
			j += 1
			if j == len(sublst):
				break
	return (result == sublst)


def containsSublist(lst, sublst):
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
	elif sys.argv[2] == "-clo":
		closed = True

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
		smth = "max"
	elif closed:
		smth = "closed"

	outName = "log_" + smth + filename.strip('.rqes') + ".txt"
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
