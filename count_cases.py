import operator
import random
from subprocess import call

files=['L3323A2.laz',  
'L4114G4.laz',  
'L4433E4.laz',  
'M4343H4.laz',  
'N4131C4.laz',  
'N4131D4.laz',  
'P3332D2.laz',  
'Q3334A1.laz',  
'V4333D1.laz',
'K4241D1.laz',  
'L3414A2.laz',  
'L4141D4.laz',  
'M3324H3.laz',  
'M4443B2.laz',  
'N4131D1.laz',  
'N4131F1.laz',  
'P3344E4.laz',  
'Q3334A2.laz',  
'V4333D3.laz',
'L3112G2.laz',  
'L3414C2.laz',  
'L4342C2.laz',  
'M4343F4.laz',
'N4131C2.laz',  
'N4131D2.laz',  
'N4131F2.laz',  
'P3434E4.laz',  
'U5141B4.laz', 
'V4343H3.laz']
		

aof = 0
feed = 0
dif = {}
usb = 0
removed_laz = 0
removed_added_pts_laz = 0

with open('taito_report_2.txt', 'r') as istr:
	for line in istr:
		if line[0:3] == 'aof':
			s = line.split(';')
			key =  s[1].split('/proj/ogiir-csc/mml/laser/Interaktiivinenluokittelu_2008-2016/')[1]
			f = int(s[3])
			u = int(s[-1])
			if f>u:
				feed+=1
				dif[key]=f-u
			elif f<u:
				usb+=1
				dif[key]=f-u
			else:
				aof+=1
		elif line[0:3] == 'rem':
			if line[-4:] == 'laz\n':
				if line[-14:-5]=='added_pts':
					removed_added_pts_laz +=1
					
				else:
					removed_laz+=1
"""
sorted_dif = sorted(dif.items(), key=operator.itemgetter(1))
rand10 =random.sample(dif,10)
min10 = [key for key, val in sorted_dif[-10:]]
max10 = [key for key, val in sorted_dif[:10]]



print min10
print max10
print rand10
for url in min10+max10+rand10:
	#call(['wget','https://tiedostopalvelu.maanmittauslaitos.fi/tp/tilauslataus/tuotteet/laser/etrs-tm35fin-n2000/mara_2m/' + url +'?api_key=bg5gt3qcn0gkv04rbukeam1btb', '-O', '/home/eannila/Downloads/sample/feed/' + url.rpartition('/')[2]])
	call(['scp',  'eannila@taito.csc.fi:/proj/ogiir-csc/mml/laser/Interaktiivinenluokittelu_2008-2016/'+url, '~/Downloads/sample/usb'])
"""
print aof, feed, usb, feed+usb

