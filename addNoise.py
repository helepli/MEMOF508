import sys 
from random import uniform
from random import randint


class AddNoise:
	
	def __init__(self, logFile, noisePercentage, artificialEvents):
		self.percentage = noisePercentage # the percentage of traces that will be impacted by noise
		#self.noiseType = noiseType # removeEvents, addEvents, swapEvents
		self.artificial = artificialEvents # list of events sepcified by the user that are not in the original log, infrequent events
		
		self.logName = ""
		self.traces = dict()
		
		self.events = []
		
		self.isMultiset = True # depends of the format of the log: if it's in multiset notation (number of occurrence of a trace next to it)
								# to be changed manually
		self.parse(logFile)
		self.impacted = [False for i in range(len(self.traces.keys()))]
		self.nbTraces = round((round(len(self.traces.keys())*noisePercentage))/3) # this might not be very serious science
		self.addNoise()
		self.write()
		
	def parse(self, logFile):
		
		try:
			log = open(logFile, encoding='utf-8')
			self.events = log.readline().strip().split(',') # list = ['a','b','c']
			print("Events present in this log: ")
			print(self.events)
			
			logContent = log.readline().strip().split('=') # L7=[(a,c)2, (a,b,c)3, (a,b,b,c)2, (a,b,b,b,b,c)1]
			self.logName = logContent[0]  # L7
			
			sets = logContent[1].strip('][').split(', ') # ['(a,c)2','(a,b,c)3','(a,b,b,c)2','(a,b,b,b,b,c)1']
			if self.isMultiset:
				counter = 0
				for i in range(len(sets)):
					sets[i] = sets[i].split(')') # sets[i] = ['(a,c', '2']
					for j in range(int(sets[i][1])):
						self.traces[counter] = sets[i][0].strip('(').split(',') # self.traces[counter] = ['a', 'c']
						counter+=1
			else:
				for i in range(len(sets)):
					self.traces[i] = sets[i].strip('()').split(',') # traces[1] = ['a', 'c']
		
			print("traces: ")
			print(self.traces)
			
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
			
	
	
	def write(self):
		try:
			output = open(self.logName+"_noisy.txt",'wt',encoding='utf-8')
			header = ','.join(self.events)		
			output.write(header+'\n') # first line: a,b,c, etc
			output.write(self.logName+'=[') # Lsomething=[	
			
			for i in self.traces.keys(): # (a,b,c), (a,c,b), etc
				trace = "("
				for j in range(len(self.traces[i])):
					if j == len(self.traces[i])-1:
						if i == len(self.traces.keys())-1:
							trace+=self.traces[i][j]+')'
						else:
							trace+=self.traces[i][j]+'), '
					else:
						trace+=self.traces[i][j]+','
				output.write(trace)
			output.write(']') # ]
			
		except IOError:
			print ("Error: can\'t create or write in output file!")
			exit()
		else:
			print ("Created and written in the file successfully")
			output.close()

			
	def addNoise(self):
		self.logName+="_swap_add_remove"
		self.removeEvents()
		self.addEvents()
		self.swapEvents()
		#~ if noiseType == "removeEvent":
			#~ self.logName+="_remove"
			#~ self.removeEvent()
		#~ elif noiseType == "addEvent":
			#~ self.logName+="_add"
			#~ self.addEvent()
		#~ elif noiseType == "removeHead":
			#~ self.removeHead()
		#~ elif noiseType == "removeBody":
			#~ self.removeBody()
		#~ elif noiseType == "swapEvents":
			#~ self.logName+="_swap"
			#~ self.swapEvents()
		#~ else:
			#~ print("This type of noise ya talkin' about is unknown to me, my fwend.")

	def removeEvents(self):
		timesToKill = self.nbTraces
		while timesToKill > 0:
			index = randint(0,len(self.traces.keys())-1)
			if not self.impacted[index]:
				indexJ = randint(0,len(self.traces[index])-1)
				self.traces[index].remove(self.traces[index][indexJ])
				
				self.impacted[index] = True
				timesToKill -= 1
		print("After slaying some innocent events:")
		print(self.traces)
		
	def addEvents(self):
		toBeAdded = list(self.events)
		if len(self.artificial) > 0:
			toBeAdded.extend(self.artificial)
		timesToKill = self.nbTraces
		while timesToKill > 0:
			index = randint(0,len(self.traces.keys())-1)
			if not self.impacted[index]:
				indexJ = randint(0,len(self.traces[index])-1)
				event = toBeAdded[randint(0,len(toBeAdded)-1)]
				self.traces[index].insert(indexJ, event)
				if (event in self.artificial) and (event not in self.events):
					self.events.append(event)
				self.impacted[index] = True
				timesToKill -= 1
		print("After adding some events that have nohing to do there:")
		print(self.traces)
		
	def swapEvents(self):
		timesToKill = self.nbTraces
		while timesToKill > 0:
			for i in self.traces.keys():
				coin = round(uniform(0,1))
				if coin == 1 and timesToKill > 0:
					dirty = False
					index = randint(0,len(self.traces.keys())-1)
					for j in range(len(self.traces[index])-1):
						if dirty or self.impacted[index]:
							break
						secondCoin = round(uniform(0,1))
						if secondCoin == 1:
							self.traces[index][j], self.traces[index][j+1] = self.traces[index][j+1], self.traces[index][j]
							dirty = True
							self.impacted[index] = True
							timesToKill -= 1
		print("After randomly swapping two consecutive events in some traces:")
		print(self.traces)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("This program needs a log.txt file as parameter and the noise percentage (a float).\nYou may specify artificial events, separated by comas (ex: a,b,c,d), for the addEvents function")
		exit()
	else:
		logFile = sys.argv[1]
		noisePercentage = float(sys.argv[2]) # between zero and one
		#noiseType = sys.argv[3]
		artificialEvents = []
		#if noiseType == "addEvent":
		if len(sys.argv) == 4:
			artificialEvents = sys.argv[3].split(',')
				
		noiseMaker = AddNoise(logFile, noisePercentage, artificialEvents)
		
