
class PetriNet:
	def __init__(self, pnFile):
		
		self.name = pnFile.strip('.dot') 

		self.transitions = [] # list of Transition objects
		self.transitionNames = []
		self.places = [] # list of Place objects: a place  = ([input transitions], [output transitions])
		self.placeNames = []
		self.arcs = [] # list of tuples: one tuple = (a place, a transition) or (a transition, a place)
		
		check = self.parse(pnFile) # parses .dot file + construct arcs list
		if check != "ok":
			print("Something went wrong with parsing, error code:"+check)
			exit()
		else:
			print("Parsing went OK")
			
		self.setPlaces() # from the arcs, makes the places list 
		self.setTransitions()
		print("Arcs:")	
		print(self.arcs)
		self.displayPlaces()
		
		

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
					self.transitionNames.append(line)
					newTransition = Transition(line)
					self.transitions.append(newTransition)
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
					
				line = log.readline().strip()
				
			
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
			return "ok"
		
	def getTransitionByName(self, name):
		for t in range(len(self.transitions)):
			if self.transitions[t].name == name:
				return self.transitions[t]
				
	def getPlaceByName(self, name):
		for t in range(len(self.places)):
			if self.places[t].name == name:
				return self.places[t]
	
	
	def getArcsWithThisPlace(self, placeName): # used by getPlaces(), returns a list of arcs with this place as input or output node
		result = []
		for arc in self.arcs:
			if placeName == arc[0] or placeName == arc[1]:
				result.append(arc)
		return result
		
	def getArcsWithThisTransition(self, transName): # used by getPlaces(), returns a list of arcs with this place as input or output node
		result = []
		for arc in self.arcs:
			if transName in arc[0] and arc[0] in self.transitionNames or transName in arc[1] and arc:
				result.append(arc)
		print(transName)
		return result
		
	def setPlaces(self):
		for i in range(len(self.placeNames)):
			newPlace = Place(self.placeNames[i], self.getArcsWithThisPlace(self.placeNames[i]))
			self.places.append(newPlace)
			
	def setTransitions(self):
		for trans in self.transitions:
			for place in self.places:
				if trans.name in place.inTrans and place not in trans.outPlaces:
					trans.setOutputPlaces(place)
					place.inTransObj.append(trans)
				elif trans.name in place.outTrans and place not in trans.inPlaces:
					trans.setInputPlaces(place)
					place.outTransObj.append(trans)
		
											
	
	def displayTransitions(self):
		print("Transitions")
		for trans in self.transitions:
			trans.display()
		
	def displayPlaces(self):
		print("Places")
		for place in self.places:
			place.display()
			
		
			
class Place:
	def __init__(self, name, arcs):
		self.name = name # name of the place
		# two lists of input transitions and output transitions NAMES
		self.inTrans = []
		self.outTrans = []
		
		self.inTransObj = [] # ACTUAL OBJECTS
		self.outTransObj = []
		
		self.token = False
		
		self.setInAndOutTransitions(arcs)
		
	def setInAndOutTransitions(self, arcs):
		for i in range(len(arcs)):
			if self.name == arcs[i][0]:
				self.outTrans.extend(arcs[i][1])
			else:
				self.inTrans.extend(arcs[i][0])
		
	def isStartPlace(self):
		return self.name == "start"
		
	def isEndPlace(self):
		return self.name == "end"
		
	def setToken(self):
		self.token = not self.token
	
	def hasToken(self):
		return self.token
	
	def display(self):
		print(self.inTrans, self.name, self.outTrans) 
		
	def getOutTransitions(self):
		return self.outTransObj
		
class Transition:
	def __init__(self, name):
		self.name = name # name of the place
		# two lists of input transitions and output transitions
		
		self.inPlaces = [] # ACTUAL OBJECTS
		self.outPlaces = []
		
	def	setInputPlaces(self, place):
		self.inPlaces.append(place)
		
	def setOutputPlaces(self, place):
		self.outPlaces.append(place)
		
	def display(self):
		for p in self.inPlaces:
			print("("+p.name+")")
		print(self.name)
		for p in self.outPlaces:
			print("("+p.name+")")
		
	def fire(self):
		canFire = True
		for place in self.inPlaces:
			if not place.hasToken():
				canFire = False
		if canFire:
			for place in self.inPlaces:
				place.setToken()
			for place in self.outPlaces:
				place.setToken()
			return self.name
		return -1 
		

		
