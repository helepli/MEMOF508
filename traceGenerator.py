import sys 
import random
from petrinet import PetriNet

class TraceGenerator:
	def __init__(self, petriNet):
		self.pn = petriNet
		
	def generateTraces(self, number):
		traces = []
		for i in range(number):
			trace = self.generateTrace()
			traces.append(trace)
		return traces
		
	def generateTrace(self):
		trace = ""
		start = pn.getPlaceByName("start")
		start.setToken()
		
		endReached = False
		places = [start]
		while not endReached:
			nextPlaces = []
			for place in places:
				transitions = place.getOutTransitions()	
				random.shuffle(transitions)
				for trans in transitions:
					result = trans.fire()
					if result != -1:
						trace += result
						nextPlaces.extend(trans.outPlaces)
			random.shuffle(nextPlaces)
			places = nextPlaces
			for place in places:
				if place.name == "end":
					endReached = True
				
		return trace



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("This program needs a .dot petri-net spec file (used by graphviz as well) as parameter")
		exit()
	else:
		pn = PetriNet(sys.argv[1])
		traceGen = TraceGenerator(pn)
		traces = traceGen.generateTraces(10)
		print(traces)
