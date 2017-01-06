import sys 
import random
from petrinet import PetriNet

class TraceGenerator:
	def __init__(self, petriNet, noisy = False, noisePercentage = 0.0):
		self.pn = petriNet
		self.noisy = noisy
		self.p = noisePercentage
		
		self.noisyTrans = ['w', 'x', 'y', 'z']
		
		
	def generateTraces(self, number, LLO = False):
		traces = []
		for i in range(number):
			if LLO:
				trace = self.generateTraceLLO()
			else:
				trace = self.generateTrace()
			traces.append(trace)
			
		if self.noisy:
			traces = self.addNoise(traces)
		return traces
		
	def generateTraceLLO(self):
		trace = []
		start = self.pn.getPlaceByName("start")
		start.setToken()
		
		endReached = False
		places = [start]
		while not endReached:
			nextPlaces = []
			nbTokens = len(places)
			for place in places:	
				transitions = place.getOutTransitions()	
				random.shuffle(transitions)
				for trans in transitions:
					consume = len(trans.outPlaces)
					if nbTokens >= consume:
						result = trans.fire()
						if result != -1:
							trace.append(result)
							nextPlaces.extend(trans.outPlaces)
							nbTokens -= consume
			random.shuffle(nextPlaces)
			places = nextPlaces
			for place in places:
				if place.name == "end":
					endReached = True
				
		return trace
		
	def generateTrace(self):
		trace = []
		start = self.pn.getPlaceByName("start")
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
						trace.append(result)
						nextPlaces.extend(trans.outPlaces)
		
			random.shuffle(nextPlaces)
			places = nextPlaces
			for place in places:
				if place.name == "end":
					endReached = True
				
		return trace
		
	def addNoise(self, traces):
		for i in range(len(traces)):
			for j in range(len(traces[i])):
				if random.random() < self.p:
					index = random.randint(0, len(self.noisyTrans)-1)
					traces[i].insert(j, self.noisyTrans[index])
		
		return traces

	def write(self, traces):
		try:
			outName = self.pn.name
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
		
		#traceGen = TraceGenerator(pn)
		traceGen = TraceGenerator(pn, True, 0.2) # noise
		
		traces = traceGen.generateTraces(20, True) # for L7
		#traces = traceGen.generateTraces(20)
		
		traceGen.write(traces)
		print(traces)
