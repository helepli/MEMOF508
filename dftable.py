import math

class DFTable:
	def __init__(self):
		
		self.individualFrequencies = dict()
		self.individualPercentages = dict()
		
		#self.miner.events ==> key : event; value : index in dfm matrix
		# used to compute a DIRECT dependency indicator (stored in the dependency matrix, below) 
		self.directlyFollowsMatrix = [[]]
		self.isDirectlyFollowedByMatrix = [[]]
		
		
		self.isIndirectlyFollowedByMatrix = [[]]
		#~ self.directOrIndirectFollowsMatrix = [[]]
		#~ self.isDirectlyOrIndirectlyFollowedByMatrix = [[]]
		
		# -> relation approximation ('=>' in heuristic miner)
		self.dependencyMatrix = [[]]
		
		# local metric LM
		self.LMMatrix = [[]]
		
		# global metric GM
		self.GMMatrix = [[]]
		
		# Confidence of a > b :  #times a > b / individual freq of a
		self.confidenceMatrix = [[]] 		

	def displayMatrix(self, matrix, eventsDict):
		events = self.makeEventsList(eventsDict)
		
		strEv = "   "+str(events[0])
		for i in range(1, len(events)):
			strEv+="    "+str(events[i])
		print(strEv)
		for i in range(len(matrix)):
			print(events[i],end=" "); print(matrix[i])
			
			
	def makeEventsList(self, eventsDict): # param events = a events dictionary key = event; value = index (in a matrix)
		eventsList = ["" for i in range(len(eventsDict))]
		for e in eventsDict.keys():
			eventsList[eventsDict[e]] = e
		return eventsList
		
	
	def getIndividualFrequencies(self, traces, eventsDict):
		for e in eventsDict.keys():
			self.individualFrequencies[e] = 0
		for i in range(len(traces)):
			for j in range(len(traces[i])): 
				event = traces[i][j]
				self.individualFrequencies[event] += 1
					
		print("Individual event frequency: ")
		print(self.individualFrequencies)
		
	def getIndividualFrequenciesBis(self, traces, eventsDict): # if it is involved in a loop, an event can have an individual percentage > 1
		# if an event happens 100000 times in one trace, then it will be counted only once as occurrence in tha log
		individualFrequencies = dict()
		for e in eventsDict.keys():
			individualFrequencies[e] = 0
		for i in range(len(traces)):
			visited = set()
			for j in range(len(traces[i])): 
				event = traces[i][j]
				if event not in visited:
					individualFrequencies[event] += 1
					visited.add(event)
					
		print("Individual event frequency BIS: ")
		print(individualFrequencies)
		return individualFrequencies
		
	def getPercentages(self, traces, eventsDict):
		self.getIndividualFrequencies(traces, eventsDict) # not used to prune unfrequent events but in matrices
		individualFrequencies = self.getIndividualFrequenciesBis(traces, eventsDict)
		
		for a in eventsDict.keys():
			aFreq = individualFrequencies[a]
			self.individualPercentages[a] = round(aFreq / float(len(traces)), 2)
			
		print("Individual percentage for each event:")
		print(self.individualPercentages)
		
		
	def makeDirectlyFollowingMatrix(self, events, traces): # and isDirectlyFollowedBy matrix
		self.isDirectlyFollowedByMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		self.directlyFollowsMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		for i in range(len(traces)):
			lenTrace = len(traces[i])-1
			for j in range(lenTrace): 
				a = events[traces[i][j]]
				b = events[traces[i][j+1]]
				self.isDirectlyFollowedByMatrix[a][b] += 1
				self.directlyFollowsMatrix[b][a] += 1
		
		print("Indexes:")
		print(events)
		print("is directly followed by:")		
		self.displayMatrix(self.isDirectlyFollowedByMatrix, events)
		#~ print("directly follows:")
		#~ self.displayMatrix(self.directlyFollowsMatrix)
		
	#~ def makeIndirectlyFollowingMatrix(self, events, traces):
		#~ self.directOrIndirectFollowsMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		#~ self.isDirectlyOrIndirectlyFollowedByMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		#~ for i in range(len(traces)):
			#~ visited = set()
			#~ for j in range(len(traces[i])): 
				#~ if traces[i][j] not in visited:
					#~ visited.add(traces[i][j])
					#~ a = events[traces[i][j]]
					#~ for k in range(j+1, len(traces[i])):
						#~ b = events[traces[i][k]]
						#~ self.isDirectlyOrIndirectlyFollowedByMatrix[a][b] += 1
						#~ self.directOrIndirectFollowsMatrix[b][a] += 1
		#~ print("Indexes:")
		#~ print(events)
		#~ print("is directly or indirectly followed by:")		
		#~ self.displayMatrix(self.isDirectlyOrIndirectlyFollowedByMatrix, events)
		#~ print("directly or indirectly follows:")
		#~ self.displayMatrix(self.directOrIndirectFollowsMatrix)
		
	def makeIndirectlyFollowingMatrix(self, events, traces): # for LLTWOs only: a => b = |a >> b| + |b >> a| / |a >> b| + |b >> a| + 1
		# where |a >> b| = occurrences of 'aba'
		self.isIndirectlyFollowedByMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		for i in range(len(traces)):
			for j in range(len(traces[i])-2): 
				if traces[i][j] == traces[i][j+2]:
					a = events[traces[i][j]]
					b = events[traces[i][j+1]]
					aprime = events[traces[i][j+2]]
					self.isIndirectlyFollowedByMatrix[a][b] += 1
		print("Indexes:")
		print(events)
		print("is indirectly followed by:")		
		self.displayMatrix(self.isIndirectlyFollowedByMatrix, events)
		
		
	def computeDependencyMatrix(self, events, traces): # a => b = |a > b| - |b > a| / |a > b| + |b > a| + 1
		self.dependencyMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		for a in events.keys():
			a_index = events[a]
			for b in events.keys():
				result = 0
				b_index = events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				if a != b:
					num = aisfb - bisfa
					denom = aisfb + bisfa + 1
					result = round(num / float(denom), 2)
				else: # a => a = |a > a| / |a > a| + 1  (this value will be high for loops of length one)
					result = aisfb / (aisfb + 1)
				self.dependencyMatrix[a_index][b_index] = result
		print("Dependency matrix (a => b):")
		self.displayMatrix(self.dependencyMatrix, events)
	
	def getDependency(self, a_index, b_index):
		return self.dependencyMatrix[a_index][b_index] 
					
	def getLLTwoDependency(self, a_index, b_index): # special treatment for loops of length two: a => b = |a >> b| + |b >> a| / |a >> b| + |b >> a| + 1
		result = 0
		aidisfb = self.isIndirectlyFollowedByMatrix[a_index][b_index] # |a >> b|
		bidisfa = self.isIndirectlyFollowedByMatrix[b_index][a_index] # |b >> a|
		num = aidisfb + bidisfa
		denom = aidisfb + bidisfa + 1
		result = round(num / float(denom), 2)
		
		return result
	
	def computeLMMatrix(self, events, traces): # LM = P - 1.96*sqrt(P*(1-P)/N+1) ; P = |a > b|/N+1 ; N = |a > b| + |b > a|
		self.LMMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		for a in events.keys():
			a_index = events[a]
			for b in events.keys():
				result = 0
				b_index = events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				N = aisfb + bisfa # N = |a > b| + |b > a|
				P = aisfb / float(N+1) # P = |a > b|/N+1
				
				result = round(P - 1.96*math.sqrt((P*(1-P))/float(N+1)), 2)
				
				self.LMMatrix[a_index][b_index] = result
				
		print("Local metric values (LM):")
		self.displayMatrix(self.LMMatrix, events)
		
		
	def computeGMMatrix(self, events, traces): # GM = (|a > b| - |b > a|) * (#traces/|a|*|b|)
		self.GMMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		nbTraces = len(traces)
		
		for a in events.keys():
			a_index = events[a]
			aFreq = self.individualFrequencies[a] # |a|
			for b in events.keys():
				result = 0
				b_index = events[b]
				bFreq = self.individualFrequencies[b] # |b|
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				
				result = round((aisfb - bisfa)*(nbTraces/float(aFreq*bFreq)), 2)
				
				self.GMMatrix[a_index][b_index] = result
				
		print("Global metric values (GM):")
		self.displayMatrix(self.GMMatrix, events)
		
	def computeConfidenceMatrix(self, events, traces): # compute the confidence of a > b : count #times a > b / individual freq of a
		self.makeDirectlyFollowingMatrix(events, traces)
		self.confidenceMatrix = [[0 for i in range(len(events))] for j in range(len(events))]
		for a in events.keys():
			a_index = events[a]
			aFreq = self.individualFrequencies[a] # |a|
			for b in events.keys():
				result = 0
				b_index = events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				
				result = round(aisfb / float(aFreq), 2)
				
				self.confidenceMatrix[a_index][b_index] = result
				
		print("confidence of |a > b| / |a| :")
		self.displayMatrix(self.confidenceMatrix, events)
	
	def getConfidence(self, a_index, b_index):
		return self.confidenceMatrix[a_index][b_index] + 0.02 # if this value must be >= 0.1 to be frequent, then 0.09 and 0.08 are accepted

	def getConfidenceOfLLTwo(self, traces, b, c): # events b, c
		# counts |b > c > b| / |b|
		bcb = 0
		for i in range(len(traces)):
			for j in range(len(traces[i])-2):
				if traces[i][j] == b and traces[i][j+1] == c and traces[i][j+2] == b:
					bcb += 1
		return round(bcb/float(self.individualFrequencies[b]), 2)
		
