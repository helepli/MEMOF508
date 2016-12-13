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
		self.LLTwos = True

		self.parse(logFile)
		self.getAllEventsFromLog()
			
		self.footprint = [['#' for i in range(len(self.events))] for j in range(len(self.events))] # nothing is connected yet
		#self.extendedFootprint = [['#' for i in range(len(self.events))] for j in range(len(self.events))] 
		#self.eventFrequency = [0 for i in range(len(self.events))] 
		self.appearsIn = dict() # keys = an event, values = list of indexes of the traces in which the event appears 
		self.occursWithDict = dict() # keys : an event, for each event : values : a list of events 
								 # with len(appearsIn[event]) <= len(appearsIn[others in this list])
		
		self.getLLOs() # LLOs must be removed from the log BEFORE the footprint matrix is built
		
		self.makeFootprint()
		#self.makeExtendedFootprint()
		#self.getEventFrequency()
		self.fillAppearsInDict()
		self.fillOccursWithDict()
		
		self.alphaAlgorithm()
		#self.addDependencies() # implicit dependencies mining
		
		self.writeGraphviz()

		
	def parse(self, logFile):
		try:
			log = open(logFile, encoding='utf-8')
			
			#evnts = log.readline()
			
			logContent = log.readline().strip().split('=') # L7=[(a,c), (a,b,c), (a,b,b,c), (a,b,b,b,b,c)]
			self.logName = logContent[0] # L7
			sets = logContent[1].strip('][').split(', ') # ['(a,c)','(a,b,c)','(a,b,b,c)','(a,b,b,b,b,c)']
			for i in range(len(sets)):
				self.traces.append(sets[i].strip('()').split(',')) # traces[1] = ['a', 'c']
			print("Traces in the log: ")
			print(self.traces)
			
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
			
	def getAllEventsFromLog(self):
		events = []
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])):
				if self.traces[i][j] not in events:
					events.append(self.traces[i][j])
		print(events)	
		self.makeEventsDict(events)
	
	def makeEventsDict(self, evnts):
		for i in range(len(evnts)):
			self.events[evnts[i]] = i
		
	def getStartAndEnd(self):
		resultTi = set()
		resultTo = set()
		for i in range(len(self.traces)):
			resultTi.add(self.traces[i][0])
			resultTo.add(self.traces[i][len(self.traces[i])-1])
		self.Ti = list(resultTi)
		self.To = list(resultTo)
		print("Start events: ")
		print(self.Ti)
		print("End events: ")
		print(self.To)
		
	def getLLOs(self):
		toBeRemoved = []
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])-1):	
				if self.traces[i][j] == self.traces[i][j+1] and not (j == 0 or j+1 == len(self.traces[i])-1): # a b b c
					h = j
					while self.traces[i][h] == self.traces[i][j] and not h == len(self.traces[i])-1: # traces now look like: a c
						toBeRemoved.append(self.traces[i][h])
						h+=1
					candidate = [self.traces[i][j-1], self.traces[i][j], self.traces[i][h]] # a, b, c
					for item in toBeRemoved:
						self.traces[i].remove(item)
					toBeRemoved = []
					if candidate not in self.LLOs:
						self.LLOs.append(candidate)
					break
		toBeRemoved = []			
		loopEvents = []
		loopContext = dict()
		i = 0
		for loop in self.LLOs:
			loopEvents.append(loop[1])
			loopContext[i] = [loop[0], loop[2]]
			i+=1
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])-1):
				event = self.traces[i][j]
				context = [self.traces[i][j-1], self.traces[i][j+1]]
				if event in loopEvents and context == loopContext[loopEvents.index(event)]:
					toBeRemoved.append(self.traces[i][j])
			for item in toBeRemoved:
				self.traces[i].remove(item)
			toBeRemoved = []
		
		print("LLOs")
		print(self.LLOs)
		print("Set of traces after removing events involved in LLOs: ")
		print(self.traces)
		
		
	def isInLLOs(self, place):
		loops = []
		for loop in self.LLOs:
			if place[0][0] == loop[0] and place[1][0] == loop[2]:
				if loop not in loops:
					loops.append(loop)
		if len(loops)!=0:
			return loops
		else:
			return -1
		
	def isALLOEvent(self, event):
		result = False
		for loop in self.LLOs:
			if event == loop[1]:
				result = True
		return result
		
	def fillOccursWithDict(self):
		
		events = [x for x in self.events.keys()]
			
		for i in range(len(events)):
			if not self.isALLOEvent(events[i]):
				self.occursWithDict[events[i]] = []
				for j in range(len(events)):  
					if events[i] != events[j]:
						iOccurs = self.appearsIn[events[i]]
						jOccurs = self.appearsIn[events[j]]
						if self.AisInB(iOccurs, jOccurs) and events[j] not in self.occursWithDict[events[i]]:  # len(iOccurs) <= len(jOccurs)
							self.occursWithDict[events[i]].append(events[j])
		print("OccursWith dictionnary: ")
		print(self.occursWithDict)
		
				
	def occursWith(self, event, other):
		occursWithEvent = self.occursWithDict[event]
		return (other in occursWithEvent)
		
		
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
					
		if self.LLTwos: # ex a b c b c b c ...b d
			for i in range(len(self.traces)):
				for j in range(len(self.traces[i])-2):
					if self.traces[i][j] == self.traces[i][j+2]:
						b = self.events[self.traces[i][j]]
						c = self.events[self.traces[i][j+1]]
						self.footprint[b][c] = ">" # b is followed by c
						self.footprint[c][b] = ">" # c is followed by b		
		
		self.displayFPM()
		
	def displayFPM(self):
		print("Events index in the FP matrix:")
		print(self.events)
		print("Footprint matrix:")
		for i in range(len(self.footprint)):
			print(self.footprint[i])
				
		
	def makeExtendedFootprint(self): # indicates if b follows a directly or later in some trace
		for i in range(len(self.traces)):
			lenTrace = len(self.traces[i])
			for j in range(lenTrace): 
				a = self.events[self.traces[i][j]]
				for k in range(j+1, lenTrace):
					b = self.events[self.traces[i][k]]
					if self.extendedFootprint[a][b] == "#": # '#' = not connected; it's the first time we see this two events next to each other
						self.extendedFootprint[a][b] = ">>" # '>>' = a is followed directly or indirectly by b
						self.extendedFootprint[b][a] = "<<" # '<<' = b directly or indirectly follows a
					elif self.extendedFootprint[a][b] == "<<": # if a follows b in some other trace
						self.extendedFootprint[a][b] = "||" # '||' = a and b are in parallel
						self.extendedFootprint[b][a] = "||" 
					
		print("extendedFootprint: ")
		print(self.extendedFootprint)		
	
	def getEventFrequency(self):
		frequencies = [0 for x in range(len(self.events))]
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])): 
				index_a = self.events[self.traces[i][j]]
				self.eventFrequency[index_a] += 1
					
		print("eventFrequency: ")
		print(self.eventFrequency)	
		
	def isAlwaysWith(self, a, b):
		indeed = True
		aIsInTraces = self.appearsIn[a]
		bIsInTraces = self.appearsIn[b]
		if len(aIsInTraces) != len(bIsInTraces):
			return False
		for trace in aIsInTraces:
			if trace not in bIsInTraces:
				indeed = False
		return indeed
		
		
	def fillAppearsInDict(self):
		events = self.events.keys()
		for e in events:
			self.appearsIn[e] = []
			for i in range(len(self.traces)):
				for j in range(len(self.traces[i])):
					if (e == self.traces[i][j]) and (i not in self.appearsIn[e]):
						self.appearsIn[e].append(i)
		print("AppearsIn dict: ")
		print(self.appearsIn)
		
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
		
		#self.getLLOs()
		
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
					break
				elif self.AisInB(place2[0], place1[0]) and self.AisInB(place2[1], place1[1]): 
					found = True
					toBeRemoved.append(place2)
					break
		for place in toBeRemoved:
			i = self.Yl.index(place)
			del self.Yl[i]
				
		
	def AisInB(self, A, B):
		isIn = True
		for a in A:
			if a not in B:
				isIn = False
		return isIn
		
		
	def addDepRecur(self, end, otherEnd, result): # recursif implicit dependencies miner, to get dependencies of any distance
		candidates = self.generateCandidates(end, otherEnd)
		print("Subtraces generated")
		print(candidates)
		for c in range(len(candidates)):
			if not self.isInSet(self.traces, candidates[c]):
				result = self.addNewPlaces(candidates, result)
				return result
		for k in range(len(self.Yl)):
			if otherEnd[1] == self.Yl[k][0]:
				otherEnd = self.Yl[k]
				self.addDepRecur(end, otherEnd, result)
		return result
		
	def addDependencies(self): # implicit dependencies mining, call the recursive function addDepRecur()
		print("Mining implicit dependencies")
		result = list(self.Yl)
		for i in range(len(self.Yl)):
			for j in range(i+1, len(self.Yl)):
				if self.Yl[i][0] == self.Yl[j][1]:
					result = self.addDepRecur(self.Yl[j], self.Yl[i], result)
					#break
				if self.Yl[i][1] == self.Yl[j][0]:
					result = self.addDepRecur(self.Yl[i], self.Yl[j], result)						
					
		self.Yl = list(result)
		print("After adding some extra dependencies:")
		print(self.Yl)				
		
	def generateCandidates(self, placei, placej):
		candidates = []
		 # Yl[i][1] == Yl[j][0]
		for i in range(len(placei[0])):
			for j in range(len(placej[1])):
				candidate = [placei[0][i], placej[1][j]]
				candidates.append(candidate)					
		
		return candidates
		
	def addNewPlaces(self, candidates, result):
		for i in range(len(candidates)):
			if self.isInSet(self.traces, candidates[i]):
				if self.isAlwaysWith(candidates[i][0], candidates[i][1]): 
					if self.isChoice(candidates[i][1]) : 
						print("The subtrace"), print(candidates[i]), print("is not in the set of traces.")  
						newPlace = [[candidates[i][0]], [candidates[i][1]]]
						if not newPlace in result:
							print("Place added to the set of places:")
							print(newPlace)
							result.append(newPlace)
		return result
		
	def isChoice(self, event):
		result = False
		for i in range(len(self.Yl)):
			if event in self.Yl[i][1]:
				if len(self.Yl[i][1]) > 1:
					for other in self.Yl[i][1]:
						if other != event and not self.occursWith(event, other) and not self.occursWith(other, event):
							result = True
		return result
		
		
	def isInSet(self, aSet, seq): # check if a sequence is a subsequence of another sequence in set of sequences
		isIn = False
		i = 0
		while not isIn and i < len(aSet):
			isIn = self.contains(aSet[i], seq)
			i+=1
		return isIn
		
	def isInDict(self, aDict, aList):
		isIn = False
		i = 0
		while not isIn and i < len(aDict.keys()):
			isIn = self.contains(aDict[i], aList)
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
	
	def writePlace(self,placeName, place, model, loops = None):
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
			
		if loops != None:
			for loop in loops:
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
			print("Number of places in this model: "+str(len(self.Yl)))
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
				loops = self.isInLLOs(place)
				if loops != -1:
					self.writePlace(places[i], place, model, loops)
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
		
