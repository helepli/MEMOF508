import math

class DFTable:
	def __init__(self, alphaMiner):
		self.miner = alphaMiner
		
		self.individualFrequency = dict()
		self.getIndividualFrequencies()
		
		#self.miner.events ==> key : event; value : index in dfm matrix
		# used to compute a DIRECT dependency indicator (stored in the dependency matrix, below) 
		self.directlyFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.isDirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.makeDirectlyFollowingMatrix()
		
		self.directOrIndirectFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.isDirectlyOrIndirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.makeIndirectlyFollowingMatrix()
		
		# -> relation approximation ('=>' in heuristic miner)
		self.dependencyMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.computeDependencyMatrix()
		
		# local metric LM
		self.LMMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.computeLMMatrix()
		
		# global metric GM
		self.GMMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.computeGMMatrix()
		
		# stupid probability of a > b : simply count #times a > b / individual freq of a
		self.stupidProbaMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.computeSPMatrix()
		
	def makeEventsList(self):
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
			self.individualFrequency[e] = 0
		for i in range(len(self.miner.traces)):
			for j in range(len(self.miner.traces[i])): 
				event = self.miner.traces[i][j]
				self.individualFrequency[event] += 1
					
		print("Individual event frequnecy: ")
		print(self.individualFrequency)	
		
	def makeDirectlyFollowingMatrix(self): # and isDirectlyFollowedBy matrix
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
		print("directly follows:")
		self.displayMatrix(self.directlyFollowsMatrix)
		
	def makeIndirectlyFollowingMatrix(self):
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
		print("directly or indirectly follows:")
		self.displayMatrix(self.directOrIndirectFollowsMatrix)
		
	def computeDependencyMatrix(self): # a => b = |a > b| - |b > a| / |a > b| + |b > a| + 1
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
	
	def getDependency(self, a, b):
		a_index = self.miner.events[a]
		b_index = self.miner.events[b]
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
		nbTraces = len(self.miner.traces)
		
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			aFreq = self.individualFrequency[a] # |a|
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
				bFreq = self.individualFrequency[b] # |b|
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				bisfa = self.isDirectlyFollowedByMatrix[b_index][a_index] # |b > a|
				
				result = round((aisfb - bisfa)*(nbTraces/float(aFreq*bFreq)), 2)
				
				self.GMMatrix[a_index][b_index] = result
				
		print("Global metric values (GM):")
		self.displayMatrix(self.GMMatrix)
		
	def computeSPMatrix(self): # compute stupid probability of a > b : count #times a > b / individual freq of a
		for a in self.miner.events.keys():
			a_index = self.miner.events[a]
			aFreq = self.individualFrequency[a] # |a|
			for b in self.miner.events.keys():
				result = 0
				b_index = self.miner.events[b]
				aisfb = self.isDirectlyFollowedByMatrix[a_index][b_index] # |a > b|
				
				result = round(aisfb / float(aFreq), 2)
				
				self.stupidProbaMatrix[a_index][b_index] = result
				
		print("Stupid proba values |a > b| / |a| :")
		self.displayMatrix(self.stupidProbaMatrix)
	
		
