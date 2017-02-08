import sys 

class GraphvizWriter:
	
	def __init__(self, alphaMiner):
		self.miner = alphaMiner
		self.writeGraphviz()	
	
	def writeGraphviz(self):
		try:
			#model = open(self.miner.logName+".dot",'wt',encoding='utf-8') #python3
			model = open(self.miner.logName+".dot",'wt') # pypy
			model.write('digraph G \n{\n graph [rankdir = "LR"]\n {\n node [shape=circle style=filled]\n start\n end\n')
			places = []
			print("Number of places in this model: "+str(len(self.miner.Yl)))
			for i in range(len(self.miner.Yl)): # add 4 places for START and END added transitions
				model.write(' c'+str(i+1)+'\n')
				places.append('c'+str(i+1))
			model.write(' }\n')
			model.write(' {\n node [fontsize=35]\n')
			
			for activity in self.miner.events.keys():
				 model.write(activity+'\n')
			model.write(' }\n')
			
			model.write('start -> START \n') 
		
			
			i = 0
			for place in self.miner.Yl:
				print(place)
				loops = self.miner.isInLLOs(place)
				if loops != -1:
					self.writePlace(places[i], place, model, loops)
				else:
					self.writePlace(places[i], place, model)
				i+=1

			if len(self.miner.To) == 1:
				model.write(self.miner.To[0]+' -> end \n}\n')
			else:
				endEvents = ""
				for i in range(len(self.miner.To)):
					if i == len(self.miner.To)-1:
						endEvents+=self.miner.To[i]
					else:
						endEvents+=self.miner.To[i]+" "
				model.write('{'+endEvents+'} -> end \n} \n') 	
		except IOError:
			print ("Error: can\'t create or write in output file!")
			exit()
		else:
			print ("Created and written in the file successfully")
			model.close()		
			
	def writePlace(self, placeName, place, model, loops = None):
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
