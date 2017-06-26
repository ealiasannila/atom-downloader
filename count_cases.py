aof = 0
removed_laz = 0
removed_added_pts_laz = 0

with open('taito_report.txt', 'r') as istr:
	for line in istr:
		if line[0:3] == 'aof':
			aof += 1
		elif line[0:3] == 'rem':
			if line[-4:] == 'laz\n':
				if line[-14:-5]=='added_pts':
					removed_added_pts_laz +=1
				else:
					removed_laz+=1

print aof, removed_laz, removed_added_pts_laz

