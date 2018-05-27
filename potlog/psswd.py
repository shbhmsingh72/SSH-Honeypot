import os
from geoip import geolite2
from iso3166 import countries
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
def sortfunc(mydict): 
	count = 0
	for key, value in sorted(mydict.iteritems(), key=lambda (k,v): (v,k), reverse = True):
		if count == 20:
			break
		count += 1	
		print "%s: %s" % (key, value)

dict1 = {}
dict2 = {}
dict3 = {}
dict4 = {}
ip1 = []
kount = 0
for root, dirs, files in os.walk("./log"):
    #print dirs
    if dirs:
    	#print dirs
    	ip1 = dirs
    	for i in dirs:
    		match = geolite2.lookup(i)
    		if match is not None:
    			#print match.country
    			try:
    				if match.country=="US":
    					print i
    				key = countries.get(match.country).name
    				print i,key
    				if key in dict3.keys():
						dict3[key] = dict3[key]+1
    				else:
						dict3[key] = 1
    			except:
    				print "Country Not Found"	
    			#print find_between(countries.get(match.country),"(name=u'","")
    for file in files:
        if file.endswith(".log"):
             name = os.path.join(root, file)
             f = open(name,"r")
             for line in f:
             	line = line.split(" ")
             	if 0 <= 1 < len(line):
             		kount+=1;
             		key1 = line[1].split(":")
             		#print key1
             		key = key1[0]
             		if key in dict1.keys():
             			dict1[key] = dict1[key]+1
             		else:
             			dict1[key] = 1
             		if 0 <= 1 < len(key1):	
             			key = key1[1]
             			if key in dict4.keys():
             				dict4[key] = dict4[key]+1
             			else:
             				dict4[key] = 1	
             		key = line[0][4:6]
             		if key in dict2.keys():
             			dict2[key] = dict2[key]+1
             		else:
             			dict2[key] = 1
print kount             			
print "Username"             			
sortfunc(dict1)
print "Password"
sortfunc(dict4)
print "Country"
sortfunc(dict3)
print "Days vs Attacks"
for key in sorted(dict2.iterkeys()):
    print "%s: %s" % (key, dict2[key])
print ip1
ip2 = []
for root, dirs, files in os.walk("./log3"):
	if dirs:
    	#print dirs
		ip2 = dirs
for root, dirs, files in os.walk("./log4"):
	if dirs:
    	#print dirs
		ip2.extend(dirs)
for root, dirs, files in os.walk("./log5"):
	if dirs:
    	#print dirs
		ip2.extend(dirs)
for root, dirs, files in os.walk("./log2"):
	if files:
    	#print dirs
		ip2.extend(dirs)		
for i in ip1:
	if i in ip2:
		print i