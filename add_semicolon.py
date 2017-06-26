pos = len('aof; /proj/ogiir-csc/mml/laser/Interaktiivinenluokittelu_2008-2016/2012/Q431/1/Q4314F4.laz')
with open('taito_report.txt', 'r') as istr:
	with open('taito_report_2.txt', 'w') as ostr:
		for line in istr:
			if line[0:3] == 'aof':
				line = line[:pos] + ';' + line[pos:]    
			ostr.write(line)
