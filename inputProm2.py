import sys 

class InputProm:
	
	def __init__(self, seqFile, logFile):
		self.logName = ""
		self.traces = dict()
		self.unfreqParallelTraces = dict()
		self.sequences = dict()
		self.events = ""
		self.mapping = True
		
		self.multiset = False # is the log in multiset notation?
		self.parse(seqFile, logFile)
		
		
		if self.mapping:
			self.removeNoise()
			#self.addDependencies()
	
		#self.write() --> self.getEvents()
		
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
	

	def getFreqSeq(self, freqSeq): # returns a dict containing the frequent sequences (logfile arg) mined from the log using GSP in RapidMiner
		freqSeq.readline() # firstline is useless
		self.sequences[0] = freqSeq.readline().strip().split()
		self.sequences[0] = self.sequences[0][3:]
		for i in range (len(self.sequences[0])):
			self.sequences[0][i] = self.sequences[0][i].strip('<>')
	
		line = freqSeq.readline().strip()
		j = 1
		while line!="":
			self.sequences[j] = line.split()
			self.sequences[j] = self.sequences[j][1:]
			for e in range (len(self.sequences[j])):
				self.sequences[j][e] = self.sequences[j][e].strip('<>')
			j+=1
			line = freqSeq.readline().strip()
			
		print("Frequent sequences : ")	
		print(self.sequences)

	def getEventsFromSeqs(self): # in the case where we only have a set of freq seq and want to give it raw to the alpha algorithm
		evnts = set()
		for i in self.sequences.keys():
			for j in range(len(self.sequences[i])):
				evnts.add(self.sequences[i][j])
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
		self.logName = logContent[0] # L7
		sets = logContent[1].strip('][').split(', ') # ['(a,c)2','(a,b,c)3','(a,b,b,c)2','(a,b,b,b,b,c)1']
		if self.multiset:
			for i in range(len(sets)):
				sets[i] = sets[i].split(')') # sets[i] = ['(ac', '2']
				sets[i] = sets[i][0].strip('(').split(',') # sets[i] = ['a', 'c']
				self.traces[i] = sets[i]	
		else:
			for i in range(len(sets)):
				self.traces[i] = sets[i].strip('()').split(',') # traces[1] = ['a', 'c']
				
		print("Traces: ")
		print(self.traces)
		
	def removeNoise(self):
		self.getMapping()
		self.checkPerTwo()
		#self.getRidOfGaps()

		
	def getMapping(self):
		result = dict()
		for i in self.traces.keys():
			result[i] = ['gap' for i in range(len(self.traces[i]))]
			for j in self.sequences.keys():
				if self.containsSubseq(self.traces[i], self.sequences[j]):
					indexes = self.getIndexes(self.traces[i], self.sequences[j])
					for index in indexes:
						result[i][index] = self.traces[i][index]
				if result[i] == self.traces[i]:
					break
		self.traces = dict(result)
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
		for i in self.traces.keys():
			for j in range(len(self.traces[i])-1):
				if self.traces[i][j] != "gap" and self.traces[i][j+1] != "gap":
					candidate = [self.traces[i][j], self.traces[i][j+1]]
					frequent = self.isInSet(self.sequences, candidate)
					if not frequent:
						self.unfreqParallelTraces[i] = self.traces[i] 
						break
				
		print("Unfrequent 'a follows b' relationships remaining after mapping: ")
		print(self.unfreqParallelTraces)

	def isInSet(self, aSet, seq): # check if a sequence is a subsequence of another sequence in a set of sequences (can be traces)
		isIn = False
		i = 0
		length = len(aSet.keys())-1
		while not isIn and i<length:
			isIn = self.containsSubseq(aSet[i], seq)
			i+=1
		return isIn
	
	#~ def getRidOfGaps(traces):
		#~ toBeRemoved = []
		#~ for i in traces.keys():
			#~ gotOne = False
			#~ j = 0
			#~ while not gotOne and j<len(traces[i]):
				#~ if traces[i][j] == "gap":
					#~ toBeRemoved.append(i)
					#~ gotOne = True
				#~ j+=1
		#~ for index in toBeRemoved:
			#~ del traces[index]
		#~ return traces
					
	
	
	
#~ 
#~ def addDependencies(traces):
	#~ result = dict(traces)
	#~ for i in traces.keys():
		#~ g = 0
		#~ for j in range(i+1, len(traces.keys())):
			#~ while g < len(traces[i]) and traces[i] != traces[j]:
				#~ for h in range (len(traces[j])):
					#~ if traces[i][g] == traces[j][h]:
						#~ candidate1 = traces[i][0:g]
						#~ candidate1.extend(traces[j][h:len(traces[j])+1])
						#~ candidate2 = traces[j][0:h]
						#~ candidate2.extend(traces[i][g:len(traces[i])+1])
						#~ if (not candidate1 in traces.values()) or (not candidate2 in traces.values()):
							#~ newbie1 = traces[i][0:g]
							#~ newbie1.extend(traces[i][g+1:len(traces[i])+1])
							#~ newbie2 = traces[j][0:h]
							#~ newbie2.extend(traces[j][h+1:len(traces[j])+1])
							#~ if newbie1 == newbie2 and not newbie1 in result.values():
								#~ result[len(result.keys())+1] = newbie1
							#~ else:
								#~ if not newbie1 in result.values():
									#~ result[len(result.keys())+1] = newbie1
								#~ if not newbie2 in result.values():
									#~ result[len(result.keys())+1] = newbie2
				#~ g+=1
	#~ print("After adding some extra dependencies:")
	#~ print(result)				
	#~ return result
	

	

#~ 
#~ def getFSLengthTwo(freqSeq):
	#~ result = dict()
	#~ for i in freqSeq.keys():
		#~ if len(freqSeq[i]) == 2:
			#~ result[i] = freqSeq[i]
	#~ return result

 
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("This program needs a sequence file and a log file as parameters")
		exit()
	else:
		seqFile = sys.argv[1]
		logFile = sys.argv[2]
		inputProm = InputProm(seqFile, logFile) 
	
#~ try:
	#~ smth = ""
	#~ result = dict()
	#~ if mapping:
		#~ smth = logName+"_map_alpha"
		#~ result = traces
	#~ else:
		#~ if maximal:
			#~ smth = "_max"
		#~ elif closed:
			#~ smth = "_closed"
		#~ if subString:
			#~ smth+="_subStr"
		#~ 
		#~ smth+= seqFile.strip('.rqes')
		#~ logName = seqFile.strip('.rqes')
		#~ result = seqs
				#~ 
	#~ outName = "log" + smth + ".txt"
	#~ alphaInput = open(outName,'wt',encoding='utf-8')
		#~ 
	#~ alphaInput.write(events+'\n') # first line: a,b,c, etc
	#~ alphaInput.write(logName+'=[') # Lsomething=[
	#~ for i in result.keys(): # (a,b,c), (a,c,b), etc
		#~ trace = "("
		#~ for j in range(len(result[i])):
			#~ if j == len(result[i])-1:
				#~ if i == len(result.keys())-1:
					#~ trace+=result[i][j]+')'
				#~ else:
					#~ trace+=result[i][j]+'), '
			#~ else:
				#~ trace+=result[i][j]+','
		#~ alphaInput.write(trace)
	#~ alphaInput.write(']') # ]
			#~ 
#~ except IOError:
	#~ print ("Error: can\'t create or write in output file!")
	#~ exit()
#~ else:
	#~ print ("Created and written in the file successfully")
	#~ alphaInput.close()
