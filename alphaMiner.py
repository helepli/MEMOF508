import sys 
from itertools import chain, combinations
from parser import Parser
from graphvizWriter import GraphvizWriter
from dftable import DFTable

class AlphaMiner:
	
	def __init__(self, parser):
		self.parser = parser
		self.logName = parser.getLogName()
		self.traces = parser.getTraces()
		self.eventsList = []
		self.events = dict() # key = event name; value = index in footprint matrix
		self.Ti = []   # startEvents
		self.To = []   # endEvents
		self.Xl = []   # places
		self.Yl = []   # maximal places
		
		self.LLOs = []
		self.LLTwos = True

		
		self.addSTARTandENDtransitions()
		self.getAllEventsFromLog()
		self.makeEventsDict()
		print("Traces in the log: ")
		print(self.traces)
			
		self.footprint = [[]] # nothing is connected yet
		self.appearsIn = dict() # keys = an event, values = list of indexes of the traces in which the event appears 
		self.occursWithDict = dict() # keys : an event, for each event : values : a list of events 
								 # with len(appearsIn[event]) <= len(appearsIn[others in this list]) in the case of an event in a loop
		
		self.dftable = None
		
	def doYourStuff(self):
		
		self.dftable.getPercentages(self.traces, self.events)
		self.pruneUnfrequentEvents() # removes rare events from log
				
		self.dftable.computeConfidenceMatrix(self.events, self.traces)	
		self.dftable.computeDependencyMatrix(self.events, self.traces)
		self.dftable.computeLMMatrix(self.events, self.traces)
		self.dftable.computeGMMatrix(self.events, self.traces)
		if self.LLTwos:
			self.dftable.makeIndirectlyFollowingMatrix(self.events, self.traces) # used in dependencies for Loops of length two
		
		
		self.getLLOs() # !!! LLOs must be removed from the log BEFORE the footprint matrix is built
		self.makeFootprint()
		self.fillAppearsInDict()
		self.fillOccursWithDict()
		
		self.alphaAlgorithm()
		self.addDependencies() # implicit dependencies mining
		
			
	def getAllEventsFromLog(self):
		for i in range(len(self.traces)):
			for j in range(len(self.traces[i])):
				if self.traces[i][j] not in self.eventsList:
					self.eventsList.append(self.traces[i][j])
		print(self.eventsList)	
		
		
	def addSTARTandENDtransitions(self):
		for i in range(len(self.traces)):
			self.traces[i].insert(0, 'START')
			self.traces[i].insert(len(self.traces[i]), 'END')
		
	
	def makeEventsDict(self):
		self.events = dict()
		for i in range(len(self.eventsList)):
			self.events[self.eventsList[i]] = i
		
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
		

	def pruneUnfrequentEvents(self): # list of events
		toBeRemoved = []
		for e in self.eventsList:
			if self.dftable.individualPercentages[e] <= 0.1: # event frequency must be >= 10% of the events in the log
				toBeRemoved.append(e)
		for e in toBeRemoved:
			self.eventsList.remove(e)
		self.removeUnfreqEventsFromTraces(toBeRemoved)
		self.makeEventsDict()
		
		
	def removeUnfreqEventsFromTraces(self, tbr): # tbr = list of events to be removed from traces because unfrequent
		for i in range(len(self.traces)):
			for rareEvent in tbr:
				self.traces[i] = [event for event in self.traces[i] if event != rareEvent]
		
	
	def getLLOs(self):
		toBeRemoved = []
		for i in range(len(self.traces)):
			lenTrace = len(self.traces[i])-1
			for j in range(lenTrace):	
				if self.traces[i][j] == self.traces[i][j+1] and not (j == 0 or j+1 == len(self.traces[i])-1) : # (a, j=b, j+1=b, c) and b_j != start or b_j+1 != end
					a = self.events[self.traces[i][j]]
					b = self.events[self.traces[i][j+1]]
					if self.confident(a , b):
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
					else:
						self.traces[i].remove(self.traces[i][j+1]) # b b is unfrequent, we let only one occurrence of b, remove the repetition
						h = j+1
						while self.traces[i][h] == self.traces[i][j+1] and not h == len(self.traces[i])-1: # traces now look like: a c
							toBeRemoved.append(self.traces[i][h])
							h+=1
						for item in toBeRemoved:
							self.traces[i].remove(item)
						toBeRemoved = []
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
		#~ print("Set of traces after removing events involved in LLOs: ")
		#~ print(self.traces)
		
		
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
		
	def isALLOEvent(self, event): # "is a LLO event": return if this event is involved in a loop of length one
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
		#~ print("OccursWith dictionnary: ")
		#~ print(self.occursWithDict)
		
				
	def occursWith(self, event, other):
		occursWithEvent = self.occursWithDict[event]
		return (other in occursWithEvent)
		
	def fillAppearsInDict(self):
		events = self.events.keys()
		for e in events:
			self.appearsIn[e] = []
			for i in range(len(self.traces)):
				for j in range(len(self.traces[i])):
					if (e == self.traces[i][j]) and (i not in self.appearsIn[e]):
						self.appearsIn[e].append(i)
		#~ print("AppearsIn dict: ")
		#~ print(self.appearsIn)
		
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
		
	def confident(self, a , b, LLTwo = False):
		if LLTwo:
			 confidenceAB = self.dftable.getConfidenceOfLLTwo(self.traces, a, b) # here, a and b are events, not indexes
		else:
			confidenceAB = self.dftable.getConfidence(a, b)
		return confidenceAB >= 0.1 # confidence value threshold
		
	def dependent(self, a, b, LLTwo = False):
		if LLTwo:
			dependencyAB = self.dftable.getLLTwoDependency(a, b)
		else:
			dependencyAB = self.dftable.getDependency(a, b)
		return dependencyAB >= 0.5 # dependency value threshold. If dependent, value close to 1. If || or #, value close to 0
		
	def makeFootprint(self): # here is all the fun	
		self.footprint = [['#' for i in range(len(self.events))] for j in range(len(self.events))]
		for i in range(len(self.traces)):
			lenTrace = len(self.traces[i])-1
			for j in range(lenTrace): 
				a = self.events[self.traces[i][j]]
				b = self.events[self.traces[i][j+1]]
				if self.confident(a, b):
					if self.footprint[a][b] == "#": # '#' = not connected; it's the first time we see this two events next to each other
						if self.dependent(a, b):
							self.footprint[a][b] = ">" # '>' = a is followed by b
							self.footprint[b][a] = "<" # '<' = b follows a
						else:
							self.footprint[a][b] = "||" # '||' = a and b are in parallel
							self.footprint[b][a] = "||" 
					elif self.footprint[a][b] == "<": # if a follows b in some other trace
						self.footprint[a][b] = "||" # '||' = a and b are in parallel
						self.footprint[b][a] = "||" 
					
		if self.LLTwos: # ex a b c b c b c ...b d
			for i in range(len(self.traces)):
				for j in range(len(self.traces[i])-2):
					if self.traces[i][j] == self.traces[i][j+2]: # b_j = b_j+2
						b = self.events[self.traces[i][j]]
						c = self.events[self.traces[i][j+1]]
						#if self.confident(b, c) and self.confident(c, b) and self.dependent(b, c, True) :
						if self.confident(self.traces[i][j], self.traces[i][j+1], True) and self.dependent(b, c, True):
							self.footprint[b][c] = ">" # b is followed by c
							self.footprint[c][b] = ">" # c is followed by b		
		
		self.displayFPM()
		
	def displayFPM(self):
		print("Events index in the FP matrix:")
		print(self.events)
		print("Footprint matrix:")
		for i in range(len(self.footprint)):
			print(self.footprint[i])
				
	
		
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
						print("The subtrace ")
						print(candidates[i])
						print(" is not in the set of traces.")  
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
	
	def setDFTable(self, dftable):
		self.dftable = dftable
					
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("This program needs a log.txt file as parameter")
		exit()
	else:
		logFile = sys.argv[1]
		parser = Parser(logFile)
		
		processMiner = AlphaMiner(parser)
		
		dftable = DFTable()
		processMiner.setDFTable(dftable)
		
		processMiner.doYourStuff()
		
		graphvizWriter = GraphvizWriter(processMiner)
