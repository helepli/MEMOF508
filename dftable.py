import math

class DFTable:
	def __init__(self, alphaMiner):
		self.miner = alphaMiner
		
		self.individualFrequencies = dict()
		self.getIndividualFrequencies()
		
		self.individualPercentages = dict() # key = a; value = |a|/#tracess
		#self.getPercentages()
		
		#self.miner.events ==> key : event; value : index in dfm matrix
		# used to compute a DIRECT dependency indicator (stored in the dependency matrix, below) 
		self.directlyFollowsMatrix = [[]]
		self.isDirectlyFollowedByMatrix = [[]]
		#self.makeDirectlyFollowingMatrix()
		
		self.directOrIndirectFollowsMatrix = [[]]
		self.isDirectlyOrIndirectlyFollowedByMatrix = [[0]]
		#self.makeIndirectlyFollowingMatrix()
		
		# -> relation approximation ('=>' in heuristic miner)
		self.dependencyMatrix = [[]]
		#self.computeDependencyMatrix()
		
		# local metric LM
		self.LMMatrix = [[]]
		#self.computeLMMatrix()
		
		# global metric GM
		self.GMMatrix = [[]]
		#self.computeGMMatrix()
		
		# Confidence of a > b :  #times a > b / individual freq of a
		self.confidenceMatrix = [[]] #[[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		#self.computeConfidenceMatrix()
		
	def makeEventsList(self):
		print("HEEEYYY")
		print(self.miner.events)
		events = ["" for i in range(len(self.miner.events))]
		for e in self.miner.events.keys():
			events[self.miner.events[e]] = e
		
		return events
		
	def displayMatrix(self, matrix):
		events = self.makeEventsList()
		
		strEv = "   "+str(events[0])
		for i in range(1, len(events)):
			strEv+="    "+str(events[i])
		print(strEv)
		for i in range(len(matrix)):
			print(events[i], end = "")
			print(matrix[i])
	
	def getIndividualFrequencies(self):
		for e in self.miner.events.keys():
			self.individualFrequencies[e] = 0
		for i in range(len(self.miner.traces)):
			for j in range(len(self.miner.traces[i])): 
				event = self.miner.traces[i][j]
				self.individualFrequencies[event] += 1
					
		print("Individual event frequency: ")
		print(self.individualFrequencies)	
		
	def getPercentages(self):
		for a in self.miner.events.keys():
			aFreq = self.individualFrequencies[a]
			self.individualPercentages[a] = round(aFreq / float(len(self.miner.traces)), 2)
		print("Individual percentage for each event:")
		print(self.individualPercentages)
		
	def makeDirectlyFollowingMatrix(self): # and isDirectlyFollowedBy matrix
		self.isDirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.directlyFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		for i in range(len(self.miner.traces)):
			lenTrace = len(self.miner.traces[i])-1
			for j in range(lenTrace): 
				a = self.miner.events[self.miner.traces[i][j]]
				b = self.miner.events[self.miner.traces[i][j+1]]
				self.isDirectlyFollowedByMatrix[a][b] += 1
				self.directlyFollowsMatrix[b][a] += 1
		
		print("Indexes:")
		print(self.miner.events)
		print("is directly followed by:")		
		self.displayMatrix(self.isDirectlyFollowedByMatrix)
		#~ print("directly follows:")
		#~ self.displayMatrix(self.directlyFollowsMatrix)
		
	def makeIndirectlyFollowingMatrix(self):
		self.directOrIndirectFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.isDirectlyOrIndirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		for i in range(len(self.miner.traces)):
			lenTrace = len(self.miner.traces[i])-1
			for j in range(lenTrace): 
				a = self.miner.events[self.miner.traces[i][j]]
				
				for k in range(j+1, lenTrace):
					if self.miner.traces[i][k] == self.miner.traces[i][j]:
						break
					else:
						b = self.miner.events[self.miner.traces[i][k]]
						self.isDirectlyOrIndirectlyFollowedByMatrix[a][b] += 1
						self.directOrIndirectFollowsMatrix[b][a] += 1
		print("Indexes:")
		print(self.miner.events)
		print("is directly or indirectly followed by:")		
		self.displayMatrix(self.isDirectlyOrIndirectlyFollowedByMatrix)
		#~ print("directly or indirectly follows:")
		#~ self.displayMatrix(self.directOrIndirectFollowsMatrix)
		
	def computeDependencyMatrix(self): # a => b = |a > b| - |b > a| / |a > b| + |b > a| + 1
		self.dependencyMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
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
		self.displayMatrix(self.dependencyMatrix)
	
	def getDependency(self, a_index, b_index):
		return self.dependencyMatrix[a_index][b_index] 
					
	def getLLTwoDependency(self, a, b): # special treatment for loops of length two: a => b = |a >> b| - |b >> a| / |a >> b| + |b >> a| + 1
		result = 0
		a_index = self.miner.events[a]
		b_index = self.miner.events[b]
		aidisfb = isDirectlyOrIndirectlyFollowedByMatrix[a_index][b_index] # |a >> b|
		bidisfa = isDirectlyOrIndirectlyFollowedByMatrix[b_index][a_index] # |b >> a|
		num = aidisfb - bidisfa
		denom = aidisfb + bidisfa + 1
		result = round(num / float(denom), 2)
		
		return result
	
	def computeLMMatrix(self): # LM = P - 1.96*sqrt(P*(1-P)/N+1) ; P = |a > b|/N+1 ; N = |a > b| + |b > a|
		self.LMMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				N = aisfb + bisfa # N = |a > b| + |b > a|
				P = aisfb / float(N+1) # P = |a > b|/N+1
				
				result = round(P - 1.96*math.sqrt((P*(1-P))/float(N+1)), 2)
				
				self.LMMatrix[a_index][b_index] = result
				
		print("Local metric values (LM):")
		self.displayMatrix(self.LMMatrix)
		
		
	def computeGMMatrix(self): # GM = (|a > b| - |b > a|) * (#traces/|a|*|b|)
		self.GMMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		nbTraces = len(self.miner.traces)
		
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			aFreq = self.individualFrequencies[a] # |a|
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
				bFreq = self.individualFrequencies[b] # |b|
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				
				result = round((aisfb - bisfa)*(nbTraces/float(aFreq*bFreq)), 2)
				
				self.GMMatrix[a_index][b_index] = result
				
		print("Global metric values (GM):")
		self.displayMatrix(self.GMMatrix)
		
	def computeConfidenceMatrix(self): # compute the confidence of a > b : count #times a > b / individual freq of a
		self.makeDirectlyFollowingMatrix()
		self.confidenceMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			aFreq = self.individualFrequencies[a] # |a|
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				
				result = round(aisfb / float(aFreq), 2)
				
				self.confidenceMatrix[a_index][b_index] = result
				
		print("confidence of |a > b| / |a| :")
		self.displayMatrix(self.confidenceMatrix)
	
	def getConfidence(self, a_index, b_index):
		return self.confidenceMatrix[a_index][b_index] + 0.02 # if this value must be >= 0.1 to be frequent, then 0.09 and 0.08 are accepted
