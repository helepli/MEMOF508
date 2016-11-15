import sys 
from itertools import chain, combinations

class AlphaMiner:
	
	def __init__(self, logFile):
		self.logName = ""
		self.traces = []
		self.events = dict()
		self.Ti = []   # startEvents
		self.To = []   # endEvents
		self.Xl = []   # places
		self.Yl = []   # maximal places
		
		self.LLOs = []

		self.parse(logFile)
		self.footprint = [['#' for i in range(len(self.events))] for j in range(len(self.events))] # nothing is connected yet
		
		
		
		self.makeFootprint()
		self.alphaAlgorithm()
		self.addDependencies()
		self.writeGraphviz()

		
	def parse(self, logFile):
		try:
			log = open(logFile, encoding='utf-8')
			evnts = log.readline().strip().split(',') # list = ['a','b','c']
			print("Events present in this log: ")
			print(evnts)
			self.makeEventsDict(evnts)
			logContent = log.readline().strip().split('=') # L7=[(a,c), (a,b,c), (a,b,b,c), (a,b,b,b,b,c)]
			self.logName = logContent[0] # L7
			sets = logContent[1].strip('][').split(', ') # ['(a,c)','(a,b,c)','(a,b,b,c)','(a,b,b,b,b,c)']
			for i in range(len(sets)):
				self.traces.append(sets[i].strip('()').split(',')) # traces[1] = ['a', 'c']
			print("traces: ")
			print(self.traces)
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
	
	def makeEventsDict(self, evnts):
		for i in range(len(evnts)):
			self.events[evnts[i]] = i
		print("self.events: ")
		print(self.events)
		
	def getStartAndEnd(self):
		resultTi = set()
		resultTo = set()
		for i in range(len(self.traces)):
			resultTi.add(self.traces[i][0])
			resultTo.add(self.traces[i][len(self.traces[i])-1])
		self.Ti = list(resultTi)
		self.To = list(resultTo)
		print("start events: ")
		print(self.Ti)
		print("end events: ")
		print(self.To)
		
	def getLLOs(self):
		toBeRemoved = []
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])-1):	
				if self.traces[i][j] == self.traces[i][j+1]: # a b b c
					h = j
					while self.traces[i][h] == self.traces[i][j]: # traces now look like: a c
						toBeRemoved.append(self.traces[i][h])
						h+=1
					candidate = [self.traces[i][j-1], self.traces[i][j], self.traces[i][h]] # a, b, c
					for item in toBeRemoved:
						self.traces[i].remove(item)
					toBeRemoved = []
					if candidate not in self.LLOs:
						self.LLOs.append(candidate)
					break
		print("LLOOOOOOOs")
		print(self.LLOs)
		
	def isInLLO(self, place):
		for loop in self.LLOs:
			if place[0][0] == loop[0] and place[1][0] == loop[2]:
				return loop
		return -1
		
	def makeFootprint(self): # here is all the fun
		for i in range(len(self.traces)):
			lenTrace = len(self.traces[i])-1
			for j in range(lenTrace): 
				a = self.events[self.traces[i][j]]
				b = self.events[self.traces[i][j+1]]
				if self.footprint[a][b] == "#": # '#' = not connected; it's the first time we see this two events next to each other
					self.footprint[a][b] = ">" # '>' = a is followed by b
					self.footprint[b][a] = "<" # '<' = b follows a
				elif self.footprint[a][b] == "<": # if a follows b in some other trace
					self.footprint[a][b] = "||" # '||' = a and b are in parallel
					self.footprint[b][a] = "||" 
		print("footprint matrix")
		print(self.footprint)
		
	def areAandBConnected(self, A, B): # A = list of input transitions and B = list of output transitions

		for event in A:
			a1 = self.events[event]
			for otherEv in A:
				a2 = self.events[otherEv]
				if self.footprint[a1][a2] != "#":
					return False
					
		for event in B:
			b1 = self.events[event]
			for otherEv in B:
				b2 = self.events[otherEv]
				if self.footprint[b1][b2] != "#":
					return False
					
		for event in A:
			a = self.events[event]
			for otherEv in B:
				b = self.events[otherEv]
				if self.footprint[a][b] != ">": # '>' = a is followed by b
					return False
		return True		
		
	def alphaAlgorithm(self):
		
		self.getStartAndEnd()
		
		self.getLLOs()
		
		eventsList = self.events.keys()
		powerSet = self.getPowerSet(eventsList)
		
		for i in range(len(powerSet)):
			A = powerSet[i]
			for j in range(len(powerSet)):
				B = powerSet[j]
				if self.areAandBConnected(A, B):
					place = [A, B]
					self.Xl.append(place)
		print("Raw set of places: ")
		print(self.Xl)
		
		#self.putBackLLOs()
		
		self.getMaximalPlaces()
		print("Maximal set of places: ")
		print(self.Yl)
		
	def getMaximalPlaces(self):
		self.Yl = list(self.Xl)
		toBeRemoved = []
		for i in range(len(self.Yl)):
			found = False
			place1 = self.Yl[i]
			for j in range(i+1,len(self.Yl)):
				place2 = self.Yl[j]
				if self.AisInB(place1[0], place2[0]) and self.AisInB(place1[1], place2[1]):
					found = True
					toBeRemoved.append(place1)
					#~ if not self.isAlreadyIn(place2, self.Yl):
						#~ self.Yl.append(place2)
					break
				elif self.AisInB(place2[0], place1[0]) and self.AisInB(place2[1], place1[1]): 
					found = True
					toBeRemoved.append(place2)
					#~ if not self.isAlreadyIn(place1, self.Yl):
						#~ self.Yl.append(place1)
					break
				#~ elif j == len(self.Yl)-1 and not found:
					#~ if not self.isAlreadyIn(place1, self.Yl):
						#~ self.Yl.append(place1)
		for place in toBeRemoved:
			i = self.Yl.index(place)
			del self.Yl[i]
				
						
	#~ def isAlreadyIn(self, newPlace, setOfPlaces):
		#~ result = False
		#~ for place in setOfPlaces:
			#~ if self.AisInB(place[0], newPlace[0]) and self.AisInB(place[1], newPlace[1]) or self.AisInB(newPlace[0], place[0]) and self.AisInB(newPlace[1], place[1]):
				#~ result = True
		#~ return result
		
	def AisInB(self, A, B):
		isIn = True
		for a in A:
			if a not in B:
				isIn = False
		return isIn
		
	def addDependencies(self):
		result = list(self.Yl)
		for i in range(len(self.Yl)):
			for j in range(i+1, len(self.Yl)):
				if self.Yl[i][0] == self.Yl[j][1]:
					candidates = self.generateCandidates(self.Yl[j], self.Yl[i])
					for c in range(len(candidates)):
						if not self.isInSet(self.traces, candidates[c]):
							result = self.addNewPlaces(candidates, result)
							break
				if self.Yl[i][1] == self.Yl[j][0]:
					candidates = self.generateCandidates(self.Yl[i], self.Yl[j])
					for c in range(len(candidates)):
						if not self.isInSet(self.traces, candidates[c]):
							result = self.addNewPlaces(candidates, result)
							break
					
		self.Yl = list(result)
		print("After adding some extra dependencies:")
		print(self.Yl)				
		
	def generateCandidates(self, placei, placej):
		candidates = []
		 # Yl[i][1] == Yl[j][0]
		for i in range(len(placei[0])):
			for c in range(len(placei[1])):
				for j in range(len(placej[1])):
					candidate = [placei[0][i], placei[1][c], placej[1][j]]
					candidates.append(candidate)					
		
		return candidates
		
	def addNewPlaces(self, candidates, result):
		for i in range(len(candidates)):
			if self.isInSet(self.traces, candidates[i]):
				newPlace = [[candidates[i][0]], [candidates[i][2]]]
				if not newPlace in result:
					print("newPlace")
					print(newPlace)
					result.append(newPlace)
		return result
		
	def isInSet(self, aSet, seq): # check if a sequence is a subsequence of another sequence in set of sequences
		isIn = False
		i = 0
		while not isIn and i < len(aSet):
			isIn = self.contains(aSet[i], seq)
			i+=1
		return isIn
	
	def contains(self, lst, sublst): # returns if a list is a sublist of another list
		result = []
		j = 0
		for i in range(len(lst)):
			if lst[i] == sublst[j]:
				result.append(sublst[j])
				j += 1
			if j == len(sublst):
				break
		return result == sublst
			
		
	def getPowerSet(self, eventsList):
		powerSet = []
		for subset in chain.from_iterable(combinations(eventsList, a) for a in range(len(eventsList)+1)):
			if len(subset) != 0:
				powerSet.append(list(subset))
		return powerSet
	
	def writePlace(self,placeName, place, model, loop = None):
		if len(place[0]) == 1:
			model.write(place[0][0]+' -> '+placeName+'\n')	#(a,b) -> place		
		else:
			events = ""
			for i in range(len(place[0])):
				if i == len(place[0])-1:
					events+=place[0][i]
				else:
					events+=place[0][i]+" " 
			model.write('{'+events+'} -> '+placeName+'\n')
			
		if loop != None:
			model.write(placeName+' -> '+loop[1]+'\n')	#place -> (c)
			model.write(loop[1]+' -> '+placeName+'\n')	#(a,b) -> place	
				
		if len(place[1]) == 1:
			model.write(placeName+' -> '+place[1][0]+'\n')	#place -> (c)
		else:
			events = ""
			for i in range(len(place[1])):
				if i == len(place[1])-1:
					events+=place[1][i]
				else:
					events+=place[1][i]+" " 
			model.write(placeName+' -> {'+events+'}\n')				
	
	def writeGraphviz(self):
		try:
			model = open(self.logName+".dot",'wt',encoding='utf-8')
			model.write('digraph G \n{\n graph [rankdir = "LR"]\n {\n node [shape=circle style=filled]\n start\n end\n')
			places = []
			print("len(self.Yl) "+str(len(self.Yl)))
			for i in range(len(self.Yl)):
				model.write(' c'+str(i+1)+'\n')
				places.append('c'+str(i+1))
			model.write(' }\n')
			model.write(' {\n node [fontsize=35]\n')
			
			for activity in self.events.keys():
				 model.write(activity+'\n')
			model.write(' }\n')
			
			startEvents = ""
			if len(self.Ti) == 1:
				model.write('start -> '+self.Ti[0]+'\n') # start -> (a,b)
			else:
				endEvents = ""
				for i in range(len(self.Ti)):
					if i == len(self.Ti)-1:
						startEvents+=self.Ti[i]
					else:
						startEvents+=self.Ti[i]+" "
				model.write('start -> {'+startEvents+'}\n')
			
			i = 0
			for place in self.Yl:
				print(place)
				loop = self.isInLLO(place)
				if loop != -1:
					self.writePlace(places[i], place, model, loop)
				else:
					self.writePlace(places[i], place, model)
				i+=1

			if len(self.To) == 1:
				model.write(self.To[0]+' -> end \n}\n')
			else:
				endEvents = ""
				for i in range(len(self.To)):
					if i == len(self.To)-1:
						endEvents+=self.To[i]
					else:
						endEvents+=self.To[i]+" "
				model.write('{'+endEvents+'} -> end \n} \n') 	
		except IOError:
			print ("Error: can\'t create or write in output file!")
			exit()
		else:
			print ("Created and written in the file successfully")
			model.close()			
					
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("This program needs a log.txt file as parameter")
		exit()
	else:
		logFile = sys.argv[1]
		processMiner = AlphaMiner(logFile)
		
