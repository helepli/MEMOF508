
import sys 

maximal = False 
closed = False
subString = False
mapping = False

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
				if supports[i] == supports[j]:
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
	lenSublst = len(getIndexes(lst, sublst))
	return (lenSublst == len(sublst))

def getIndexes(lst, sublst): # returns a list of positions in which the items in a subsequence appear in a sequence
	result = []
	j = 0
	for i in range(len(lst)):
		if lst[i] == sublst[j]:
			result.append(i)
			j += 1
			if j == len(sublst):
				break
	return result
	
def isInSet(aSet, seq): # check if a sequence is a subsequence of a trace in a set of traces
	isIn = False
	i = 0
	length = len(aSet.keys())-1
	while not isIn and i<length:
		isIn = isSubseq(aSet[i], seq)
		i+=1
	return isIn

def containsSubstring(lst, sublst):
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in range(len(lst)-n+1))
    
def getFreqSeq(freqSeq): # returns a dict containing the frequent sequences (logfile arg) mined from the log using GSP in RapidMiner
	freqSeq.readline() # firstline is useless
	seqs = dict()
	seqs[0] = freqSeq.readline().strip().split()
	if closed:
		supports = []
		supports.append(float(seqs[0][2].strip(':')))
	seqs[0] = seqs[0][3:]
	for i in range (len(seqs[0])):
		seqs[0][i] = seqs[0][i].strip('<>')
	
	line = freqSeq.readline().strip()
	j = 1
	while line!="":
		seqs[j] = line.split()
		if closed:
			supports.append(float(seqs[j][0].strip(':')))
		seqs[j] = seqs[j][1:]
		for e in range (len(seqs[j])):
			seqs[j][e] = seqs[j][e].strip('<>')
		j+=1
		line = freqSeq.readline().strip()
	print(seqs)
	return seqs

def getFSLengthTwo(freqSeq):
	result = dict()
	for i in freqSeq.keys():
		if len(freqSeq[i]) == 2:
			result[i] = freqSeq[i]
	return result

def preProcess(traces, freqSeq):
	#result = checkPerTwo(traces, freqSeq)
	#FSLengthTwo = getFSLengthTwo(freqSeq)
	result = addDependencies(traces)
	return result
	
def checkPerTwo(traces, freqSeq): # this should get rid of fake parallelism for example
	result = dict()
	frequent = True
	print (freqSeq)
	for i in traces.keys():
		for j in range(len(traces[i])-1):
			candidate = [traces[i][j], traces[i][j+1]]
			frequent = isInSet(freqSeq, candidate)
			if not frequent:
				break
		if frequent:
			result[i] = traces[i]
	print("After pruning traces containing non frequent 'a follows b' relationships remaining after mapping: ")
	print(result)
	return result

def addDependencies(traces):
	result = dict(traces)
	for i in traces.keys():
		g = 0
		for j in range(i+1, len(traces.keys())):
			while g < len(traces[i]) and traces[i] != traces[j]:
				for h in range (len(traces[j])):
					if traces[i][g] == traces[j][h]:
						print("tracei")
						print(traces[i])
						print("tracej")
						print(traces[j])
						print(traces[i][g])
						candidate1 = traces[i][0:g]
						candidate1.extend(traces[j][h:len(traces[j])+1])
						print("candidate1")
						print(candidate1)
						candidate2 = traces[j][0:h]
						candidate2.extend(traces[i][g:len(traces[i])+1])
						print("candidate2")
						print(candidate2)
						if (not candidate1 in traces.values()) or (not candidate2 in traces.values()):
							newbie1 = traces[i][0:g]
							newbie1.extend(traces[i][g+1:len(traces[i])+1])
							print("newbie1")
							print(newbie1)
							newbie2 = traces[j][0:h]
							newbie2.extend(traces[j][h+1:len(traces[j])+1])
							print("newbie2")
							print(newbie2)
							if newbie1 == newbie2 and not newbie1 in result.values():
								result[len(result.keys())+1] = newbie1
							else:
								if not newbie1 in result.values():
									result[len(result.keys())+1] = newbie1
								if not newbie2 in result.values():
									result[len(result.keys())+1] = newbie2
				g+=1
	print("After adding some extra dependencies:")
	print(result)				
	return result
	
    
def getTraces(log): # returns a dict containing the traces in the original logfile 
	events = log.readline().strip().replace(',', ';') # a,b,c
	print("Events present in this log are: "+events)
	logContent = log.readline().strip().split('=') # L7=[(a,c)2, (a,b,c)3, (a,b,b,c)2, (a,b,b,b,b,c)1]
	print("Log content: ")
	print(logContent)
	logName = logContent[0] # L7
	sets = logContent[1].strip('][').split(', ') # ['(a,c)2','(a,b,c)3','(a,b,b,c)2','(a,b,b,b,b,c)1']
	traces = dict()
	for i in range(len(sets)):
		sets[i] = sets[i].split(')') # sets[i] = ['(ac', '2']
		sets[i] = sets[i][0].strip('(').split(',') # sets[i] = ['a', 'c']
		print(sets[i])
		traces[i] = sets[i]		
	return traces

def getMapping(traces, seqs):
	result = dict()
	for i in traces.keys():
		result[i] = ['gap' for i in range(len(traces[i]))]
		for j in seqs.keys():
			if isSubseq(traces[i] ,seqs[j]):
				indexes = getIndexes(traces[i] ,seqs[j])
				for index in indexes:
					result[i][index] = traces[i][index]
			if result[i] == traces[i]:
				break
	print("Result of the mapping:")
	print(result)
	return result
		
    	     
if len(sys.argv) < 2:
	print("This program needs a log.txt file as parameter")
	exit()
else:
	seqFile = sys.argv[1]
if len(sys.argv) >= 3:
	maximal = sys.argv[2] == "-max"
	closed = sys.argv[2] == "-clo"
	if len(sys.argv) == 4:
		subString = sys.argv[3] == "-str"
		mapping = sys.argv[3] == "-map"
		if mapping:
			logFile = sys.argv[2]

try:
	freqSeq = open(seqFile, encoding='utf-8')
	seqs = getFreqSeq(freqSeq)
	if mapping:
		log = open(logFile, encoding='utf-8')
		traces = getTraces(log)
		traces = getMapping(traces, seqs)
		traces = preProcess(traces, seqs)
	
	if maximal:
		seqs = getMaximal(seqs)
		print("After pruning non-maximal sequences: ") 			
		print(seqs)
	elif closed:
		print("Supports: ")
		print(supports)
		seqs = getClosed(seqs)
		print("After pruning non-closed sequences: ")
		print(seqs)
	
except IOError:
	print ("Error: can\'t find file or read content!")
	exit()
else:
	print ("Opened and read the file successfully")
	freqSeq.close()
	if mapping:
		log.close()
	
	
try:
	smth = ""
	if maximal:
		smth = "_max"
	elif closed:
		smth = "_closed"
	if subString:
		smth+="_subStr"

	outName = "log" + smth + seqFile.strip('.rqes') + ".txt"
	promInput = open(outName,'wt',encoding='utf-8')
	promInput.write('traceID;eventID \n')
	traceID = 0
	result = dict()
	if mapping:
		result = traces
	else:
		result = seqs
	for i in result.keys():
		for j in range(len(result[i])):
			promInput.write('t'+str(traceID)+';'+result[i][j]+'\n')
		traceID += 1
except IOError:
	print ("Error: can\'t create or write in output file!")
	exit()
else:
	print ("Created and written in the file successfully")
	promInput.close()
