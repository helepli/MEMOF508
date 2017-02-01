import sys 

class Parser:
	
	def __init__(self, logFile):
		self.traces = []
		self.logName = ""
		self.parse(logFile)

	def parse(self, logFile):
		try:
			log = open(logFile, encoding='utf-8')
			
			#evnts = log.readline()
			
			logContent = log.readline().strip().split('=') # L7=[(a,c), (a,b,c), (a,b,b,c), (a,b,b,b,b,c)]
			self.logName = logContent[0] # L7
			sets = logContent[1].strip('][').split(', ') # ['(a,c)','(a,b,c)','(a,b,b,c)','(a,b,b,b,b,c)']
			for i in range(len(sets)):
				self.traces.append(sets[i].strip('()').split(',')) # traces[1] = ['a', 'c']
			
			
		except IOError:
			print ("Error: can\'t find file or read content!")
			exit()
		else:
			print ("Opened and read the file successfully")
			log.close()
			
	def getTraces(self):
		return self.traces
		
	def getLogName(self):
		return self.logName
