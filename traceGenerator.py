import sys 
import random
from petrinet import PetriNet

class TraceGenerator:
	def __init__(self, petriNet, noisy = False):
		self.pn = petriNet
		self.noisy = noisy
		
		
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

	def write(self, traces):
		try:
			outName = pn.name
			if self.noisy:
				outName+='_noisy'
			output = open(outName + '.txt','wt')
			
			output.write(outName+'=[')
			for i in range(len(traces)):
				trace = '('
				for j in range(len(traces[i])):
					if j == len(traces[i])-1:
						if i == len(traces)-1:
							trace+=traces[i][j]+')'
						else:
							trace+=traces[i][j]+'), '
					else:
						trace+=traces[i][j]+','
				output.write(trace)
			output.write(']')		
		except IOError:
			print ("Error: can\'t create or write in output file!")
			exit()
		else:
			print ("Created and written in the file successfully")
			output.close()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("This program needs a .dot petri-net spec file (used by graphviz as well) as parameter")
		exit()
	else:
		pn = PetriNet(sys.argv[1])
		traceGen = TraceGenerator(pn)
		traces = traceGen.generateTraces(10)
		traceGen.write(traces)
		print(traces)
