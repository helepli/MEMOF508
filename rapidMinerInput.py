# log format : 
# first line : events
# second line : log (!!whitespace after comas inside '[]', but no whitespace after comas inside '()')
# ex :
# a,b,c
# L7=[(a,c)2, (a,b,c)3, (a,b,b,c)2, (a,b,b,b,b,c)1]

import sys  

multiset = False 
             
if len(sys.argv)<2:
	print("This program needs a log.txt file as parameter")
	exit()
else:
	filename = sys.argv[1]

try:
	log = open(filename, encoding='utf-8')
	events = log.readline().strip().replace(',', ';') # a,b,c
	print("Events present in this log are: "+events)
	logContent = log.readline().strip().split('=') # L7=[(a,c)2, (a,b,c)3, (a,b,b,c)2, (a,b,b,b,b,c)1]
	print("Log content: ")
	print(logContent)
	logName = logContent[0] # L7
	
	sets = logContent[1].strip('][').split(', ') # ['(a,c)','(a,c)','(a,b,c)','(a,b,c)','(a,b,c)', etc.] or 
												 # ['(a,c)2','(a,b,c)3','(a,b,b,c)2','(a,b,b,b,b,c)1'] (multiset notation)
	
		
	
except IOError:
	print ("Error: can\'t find file or read content!")
else:
	print ("Opened and read the file successfully")
	log.close()

try:
	GSPinput = open(logName+'_GSPinput.txt','wt',encoding='utf-8')
	GSPinput.write('customerID;timestamp;'+events+ '\n')
	events = events.split(';') # events = ['a','b','c']
	nbrEvents = len(events)
	
	if multiset: # ex : "(a,c)2"
		seqID = 0
		for setID in range (len(sets)): 
			seti = sets[setID].strip('(').split(')') # ['a,c', '2']
			tr = seti[0].split(',') # traces = ['a','c']
			for i in range (int(seti[1])):
				seqID += 1
				for tID in range (len(tr)):
					binary = ''
					for e in range(nbrEvents):
						if tr[tID] == events[e]:
							if e == nbrEvents-1:
								binary+='1'
							else:
								binary+='1;'
						else:
							if e == nbrEvents-1:
								binary+='0'
							else:
								binary+='0;'
					GSPinput.write('trace'+str(seqID)+';'+str(tID)+';'+binary+'\n') 
		
	else: # sets[ID] = "(a,c)"
		for setID in range (len(sets)):
			tr = sets[setID].strip('()').split(',')
			for t in range(len(tr)):
				binary = ''
				for e in range(nbrEvents):
					if tr[t] == events[e]:
						if e == nbrEvents-1:
							binary+='1'
						else:
							binary+='1;'
					else:
						if e == nbrEvents-1:
							binary+='0'
						else:
							binary+='0;'
				GSPinput.write('trace'+str(setID)+';'+str(t)+';'+binary+'\n')		
				
except IOError:
	print ("Error: can\'t create or write in output file!")
else:
	print ("Created and written in the file successfully")
	GSPinput.close()




