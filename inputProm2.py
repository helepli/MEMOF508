import sys 

class InputProm:
	
	def __init__(self, seqFile, logFile):
		self.logName = logFile
		self.traces = []
		self.unfreqParallelTraces = []
		self.sequences = []
		self.events = ""
		self.mapping = True
		
		self.multiset = False # is the log in multiset notation?
		self.parse(seqFile, logFile)
		
		if self.mapping:
			self.removeNoise()
			self.addDependencies()
	
		self.write() 
		
	def parse(self, seqFile, logFile):
		try:
			freqSeq = open(seqFile, encoding='utf-8')
			self.getFreqSeq(freqSeq)
			
			if self.mapping:
				log = open(logFile, encoding='utf-8')
				self.getTraces(log)
			else:
				self.getEventsFromSeqs()
	
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			freqSeq.close()
			if self.mapping:
				log.close()
	
	def write(self):
		try:	
			outName = "log" + self.logName 
			output = open(outName,'wt',encoding='utf-8')
			
			self.getEvents(self.traces)	
			output.write(self.events+'\n') # first line: a,b,c, etc
			output.write(self.logName.strip(".txt")+'=[') # Lsomething=[
			for i in range(len(self.traces)): # (a,b,c), (a,c,b), etc
				trace = "("
				for j in range(len(self.traces[i])):
					if j == len(self.traces[i])-1:
						if i == len(self.traces)-1:
							trace+=self.traces[i][j]+')'
						else:
							trace+=self.traces[i][j]+'), '
					else:
						trace+=self.traces[i][j]+','
				output.write(trace)
			output.write(']') # ]
					
		except IOError:
			print ("Error: can\'t create or write in output file!")
			exit()
		else:
			print ("Created and written in the file successfully")
			output.close()
		

	def getFreqSeq(self, freqSeq): # returns a dict containing the frequent sequences (logfile arg) mined from the log using GSP in RapidMiner
		freqSeq.readline() # firstline is useless
		self.sequences.append(freqSeq.readline().strip().split())
		self.sequences[0] = self.sequences[0][3:]
		for i in range (len(self.sequences[0])):
			self.sequences[0][i] = self.sequences[0][i].strip('<>')
	
		line = freqSeq.readline().strip()
		j = 1
		while line!="":
			self.sequences.append(line.split())
			self.sequences[j] = self.sequences[j][1:]
			for e in range (len(self.sequences[j])):
				self.sequences[j][e] = self.sequences[j][e].strip('<>')
			j+=1
			line = freqSeq.readline().strip()
			
		print("Frequent sequences : ")	
		print(self.sequences)

	def getEvents(self, lstOflsts): # first line of output log, used in write function
		evnts = set()
		for i in range(len(lstOflsts)):
			for j in range(len(lstOflsts[i])):
				evnts.add(lstOflsts[i][j])
		evnts = list(evnts)
		for e in range(len(evnts)):
			if e == len(evnts):
				self.events += evnts[e]
			else:
				self.events += evnts[e]+','				

	def getTraces(self, log): # returns a dict containing the traces in the original logfile 
		#events = log.readline().strip() # a,b,c  -> should be done after removing the noise and stuff
		_ = log.readline() # osef for now
		logContent = log.readline().strip().split('=') # L7=[(a,c)2, (a,b,c)3, (a,b,b,c)2, (a,b,b,b,b,c)1]
		print("logContent ")
		print(logContent)
		#self.logName = logContent[0] # L7
		sets = logContent[1].strip('][').split(', ') # ['(a,c)2','(a,b,c)3','(a,b,b,c)2','(a,b,b,b,b,c)1']
		if self.multiset:
			for i in range(len(sets)):
				sets[i] = sets[i].split(')') # sets[i] = ['(ac', '2']
				sets[i] = sets[i][0].strip('(').split(',') # sets[i] = ['a', 'c']
				self.traces.append([i])	
		else:
			for i in range(len(sets)):
				self.traces.append(sets[i].strip('()').split(','))# traces[1] = ['a', 'c']
				
		print("Traces: ")
		print(self.traces)
		
	def removeNoise(self):
		self.getMapping()
		self.getRidOfGaps()
		self.checkPerTwo()
		self.getMaximalOnes()
		self.keepOnlyOne()

		
	def getMapping(self):
		result = []
		for i in range(len(self.traces)):
			result.append(['gap' for i in range(len(self.traces[i]))])
			for j in range(len(self.sequences)):
				if self.containsSubseq(self.traces[i], self.sequences[j]):
					indexes = self.getIndexes(self.traces[i], self.sequences[j])
					for index in indexes:
						result[i][index] = self.traces[i][index]
				if result[i] == self.traces[i]:
					break
		self.traces = list(result)
		print("Result of the mapping:")
		print(self.traces)
		
	def containsSubseq(self, lst, sublst):
		lenSublst = len(self.getIndexes(lst, sublst))
		return (lenSublst == len(sublst))

	def getIndexes(self, lst, sublst): # returns a list of positions in which the items in a subsequence appear in a sequence
		result = []
		j = 0
		for i in range(len(lst)):
			if lst[i] == sublst[j]:
				result.append(i)
				j += 1
			if j == len(sublst):
				break
		return result
		
	def checkPerTwo(self): # this should get rid of fake parallelism for example
		frequent = True
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])-1):
				#if self.traces[i][j] != "gap" and self.traces[i][j+1] != "gap":
				candidate = [self.traces[i][j], self.traces[i][j+1]]
				frequent = self.isInSet(self.sequences, candidate)
				if not frequent:
					self.unfreqParallelTraces.append(self.traces[i]) 
					break
					
		self.traces = [trace for trace in self.traces if trace not in self.unfreqParallelTraces]
		print("Unfrequent 'a follows b' relationships remaining after mapping: ")
		print(self.unfreqParallelTraces)
		print("What's left of the traces in the log: ")
		print(self.traces)
		print(len(self.traces))
		
	def getMaximalOnes(self):
		toBeRemoved = []
		for i in range(len(self.traces)):
			for j in range(len(self.traces)):
				if self.containsSubseq(self.traces[j], self.traces[i]) and len(self.traces[i]) < len(self.traces[j]) and not (self.traces[i] in toBeRemoved): 
					toBeRemoved.append(self.traces[i])
					
		print(toBeRemoved)
		self.traces = [trace for trace in self.traces if trace not in toBeRemoved]
		print("traces left after removing non maximal ones: ")
		print(self.traces)
		
	def keepOnlyOne(self):
		representatives = []
		i = 0
		representatives.append(self.traces[i])
		one = self.traces[i]
		while i < (len(self.traces)):
			if one != self.traces[i] and not self.isInSet(representatives, self.traces[i]): 
				representatives.append(self.traces[i])
				one = self.traces[i]
			i+=1
		self.traces = list(representatives)
		print("Representatives: ")			
		print(representatives)
		

	def isInSet(self, aSet, seq): # check if a sequence is a subsequence of another sequence in a dictionary
		isIn = False
		i = 0
		length = len(aSet)-1
		while not isIn and i<length:
			isIn = self.containsSubseq(aSet[i], seq)
			i+=1
		return isIn
	
	def getRidOfGaps(self):
		toBeRemoved = []
		for i in range(len(self.traces)):
			gotOne = False
			j = 0
			while not gotOne and j<len(self.traces[i]):
				if self.traces[i][j] == "gap":
					toBeRemoved.append(self.traces[i])
					gotOne = True
				j+=1
		for trace in toBeRemoved:
			self.traces.remove(trace)
		print("After removing all infrequent events: ")
		print(self.traces)
		print(len(self.traces))
					

	def addDependencies(self):
		result = list(self.traces)
		for i in range(len(self.traces)):
			g = 0
			for j in range(i+1, len(self.traces)):
				while g < len(self.traces[i]) and self.traces[i] != self.traces[j]:
					for h in range (len(self.traces[j])):
						if self.traces[i][g] == self.traces[j][h]:
							candidate1 = self.traces[i][0:g]
							candidate1.extend(self.traces[j][h:len(self.traces[j])+1])
							candidate2 = self.traces[j][0:h]
							candidate2.extend(self.traces[i][g:len(self.traces[i])+1])
							if (not candidate1 in self.traces) or (not candidate2 in self.traces):
								newbie1 = self.traces[i][0:g]
								newbie1.extend(self.traces[i][g+1:len(self.traces[i])+1])
								newbie2 = self.traces[j][0:h]
								newbie2.extend(self.traces[j][h+1:len(self.traces[j])+1])
								if newbie1 == newbie2 and not newbie1 in result:
									result.append(newbie1)
								else:
									if not newbie1 in result:
										result.append(newbie1)
									if not newbie2 in result:
										result.append(newbie2)
					g+=1
		self.traces = list(result)
		print("After adding some extra dependencies:")
		print(self.traces)				
		
 
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("This program needs a sequence file and a log file as parameters")
		exit()
	else:
		seqFile = sys.argv[1]
		logFile = sys.argv[2]
		inputProm = InputProm(seqFile, logFile) 
	

