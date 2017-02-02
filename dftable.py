
class DFTable:
	def __init__(self, alphaMiner):
		self.miner = alphaMiner
		
		self.individualFrequency = dict()
		self.getIndividualFrequencies()
		
		#self.miner.events ==> key : event; value : index in dfm matrix
		self.directlyFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.isDirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.makeDirectlyFollowingMatrix()
		
		self.directOrIndirectFollowsMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.isDirectlyOrIndirectlyFollowedByMatrix = [[0 for i in range(len(self.miner.events))] for j in range(len(self.miner.events))]
		self.makeIndirectlyFollowingMatrix()
	
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
				print(self.miner.traces[i][j])
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
		print("directly follows:")
		self.displayMatrix(self.directOrIndirectFollowsMatrix)
		
	def displayMatrix(self, matrix):
		for i in range(len(matrix)):
			print(matrix[i])
