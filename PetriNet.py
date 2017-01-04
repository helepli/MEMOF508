import sys 
import random
import numpy as np

class PetriNet:
	def __init__(self, pnFile):
		self.transitions = [] # events, list of letters
		self.inputPlaces = dict() # key : transition, value : number of input places
		self.startTransitions = []
		self.endTransitions = []
		self.placeNames = []
		self.places = [] # list of Places: a place  = ([input transitions], [output transitions])
		self.arcs = [] # list of tuples: one tuple = (a place, a transition) or (a transition, a place)
		
		check = self.parse(pnFile) # parses .dot file + construct arcs list
		if check != "ok":
			print("Something went wrong with parsing, error code:"+check)
			exit()
		else:
			print("Parsing went OK")
			
		self.getPlaces() # from the arcs, makes the places list 
		

	def parse(self, pnFile):
		try:
			log = open(pnFile)
			
			line = log.readline() # digraph G 
			line = log.readline() # {
			line = log.readline() #graph [rankdir = "LR"]
			line = log.readline() # {
			line = log.readline().strip() # node [shape=circle style=filled]
			if line == "node [shape=circle style=filled]":
				line = log.readline().strip()
				while line != "}":
					self.placeNames.append(line)
					line = log.readline().strip()
			else:
				return 'node [shape=circle style=filled] not found, line = '+ line
			
			line = log.readline() # {
			line = log.readline().strip() # node [fontsize=35]
			if line == "node [fontsize=35]":
				line = log.readline().strip()
				while line != "}":
					self.transitions.append(line)
					self.inputPlaces[line] = 0
					line = log.readline().strip()
			else:
				return 'node [fontsize=35] not found, line = '+ line
					
			line = log.readline().strip()	# start -> a, for example	
			while line != "}":
				line = line.split(' -> ')
				if line[0] not in self.placeNames:
					transition = line[0].strip('{}').split(' ')
					place = line[1]
					self.arcs.append((transition, place))
				elif line[1] not in self.placeNames:
					transition = line[1].strip('{}').split(' ')
					place = line[0]
					self.arcs.append((place, transition))
					for t in transition:
						self.inputPlaces[t] += 1
				
				if line[0] == 'start':
					self.startTransitions.extend(line[1].strip('{}').split(' '))
				if line[1] == 'end':
					self.endTransitions.extend(line[0].strip('{}').split(' '))
					
				line = log.readline().strip()
			print("Transitions:")	
			print(self.transitions)
			print("Start transitions:")
			print(self.startTransitions)
			print("End transitions:")
			print(self.endTransitions)
			print("input places:")	
			print(self.inputPlaces)
			print("Arcs:")	
			print(self.arcs)
			
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
			return "ok"
			
	def getPlaces(self):
		for p in self.placeNames:
			inTrans = []
			outTrans = []
			arcs = self.getArcsWithThisPlace(p)
			lenArcs = len(arcs)
			i = 0
			temp = []
			while lenArcs > 0:
			
			 	if p == arcs[i][0]:
					outTrans = arcs[i][1]
					lenArcs -= 1
				if p == arcs[i][1]:
					inTrans = arcs[i][0]
					lenArcs -= 1
				if len(inTrans) != 0 and len(outTrans) != 0 or p == "start" or p == "end":
					if [p, inTrans, outTrans] not in temp:
						newPlace = Place(p, inTrans, outTrans)
						self.places.append(newPlace)
						temp.append([p, inTrans, outTrans])
				i+=1
				
		print("Places:")
		self.displayPlaces(self.places)
	
	def displayPlaces(self, setOfPlaces): # print places because a place is an object of a class Place
		for place in setOfPlaces:
			if place.name != "start":
				inTrans = "("
				for t in range(len(place.inTrans)):
					if t == len(place.inTrans)-1:
						inTrans += place.inTrans[t]+")"
					else:
						inTrans += place.inTrans[t]+", "
			else:
				inTrans = ""
			if place.name != "end":
				outTrans ="("
				for t in range(len(place.outTrans)):
					if t == len(place.outTrans)-1:
						outTrans += place.outTrans[t]+")"
					else:
						outTrans += place.outTrans[t]+", "
			else:
				outTrans = ""
					
			print("["+inTrans+", "+place.name+", "+outTrans+"]")
			
			
	def getArcsWithThisPlace(self, placeName): # used by getPlaces(), returns a list of arcs with this place as input or output node
		result = []
		for arc in self.arcs:
			if placeName == arc[0] or placeName == arc[1]:
				result.append(arc)
		return result
	
	def generateSequences(self, number): # number of sequences to generate
		sequences = []
		for i in range(number):
			
			sequence = []
			places = []
			for pi in range(len(self.places)):
				if self.places[pi].name == "start":
					places.append(self.places[pi])
					
					
			endReached = False
			
			for pi in range(len(places)):
				if places[pi].name == "end":
					endReached = True
				
			
			nbTokens = 0
			while not endReached:			
				chosenTransitions = []
				random.shuffle(places)
				nbTokens += len(places)
		
				for pi in range(len(places)):
					transitions = places[pi].outTrans
					
					if nbTokens > 0 and len(transitions) > 0 and not endReached:
						if len(transitions) > 1:
							event = np.random.choice(transitions)
							while nbTokens < self.inputPlaces[event]:
								event = np.random.choice(transitions)
							
							if event not in chosenTransitions:
								chosenTransitions.append(event)
								nbTokens -= self.inputPlaces[event]
								if event in self.endTransitions:
									endReached = True 
						else:
							if nbTokens >=  self.inputPlaces[transitions[0]] and transitions[0] not in chosenTransitions:
								chosenTransitions.append(transitions[0])
								nbTokens -= self.inputPlaces[transitions[0]]
								if transitions[0] in self.endTransitions:
									endReached = True
								
				sequence.extend(chosenTransitions)
				#~ print(nbTokens)
				#~ print(sequence)
				#~ print(endReached)
							
				places = []
				for trans in chosenTransitions:
					places.extend(self.getPlacesWithInputTrans(trans))
				
				#~ for pi in range(len(places)):
					#~ if places[pi].name == "end" and loopCredit == 0:
						#~ endReached = True
					#~ elif places[pi].name == "end" and loopCredit > 0:
						#~ loopCredit -= 1
			
			sequences.append(sequence)
			
		return sequences	
	
	def getPlacesWithInputTrans(self, inTrans):
		result = set()
		for place in self.places:
			if inTrans in place.inTrans:
				result.add(place)
				
		return list(result) 
	
	
			
			
class Place:
	def __init__(self, name, inTrans, outTrans):
		self.name = name # name of the place
		# two lists of input transitions and output transitions
		self.inTrans = inTrans
		self.outTrans = outTrans
	

	

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("This program needs a .dot petri-net spec file (used by graphviz as well) as parameter")
		exit()
	else:
		pn = PetriNet(sys.argv[1])
		
		sequences = pn.generateSequences(20)
		print("Sequences:")
		print(sequences)
