import feedparser
import xml.etree.ElementTree as ET
import os
import urllib
from subprocess import call
from sets import Set
from datetime import datetime

def add_params(url, params):
	if params:
		url +='?'	
		for p in params:
			url += p
			url += '&'
		url = url[:-1]
	return url

def is_in_sets(sets, e):
	for s in sets:
		if e in s:
			return True
	return False

def check_local_files(rootdir, feed_sets, removed_set):
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			fn = os.path.join(subdir, file)
			if not is_in_sets(feed_sets, fn):
				removed_set[fn] = ''
	
def print_set(header, st):
	print ''
	print str(len(st))+' '+ header
	for f in st:
		print '	', f	


def print_report(headers, sets):
	for st, hd in zip(sets, headers):
		print_set(hd,st)

def check_newer(local, dl_link, update_set, aof_set, conflict_set, matching_set):
	
	mtime = os.path.getmtime(local)
	local_time = datetime.utcfromtimestamp(mtime)
	local_size = os.path.getsize(local)	
	
	url_meta = urllib.urlopen(dl_link).info()
	feed_time = datetime.strptime(url_meta.getheader('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z')
	feed_size = int(url_meta.getheader('Content-Length'))

	if local_time == feed_time and local_size == feed_size:
		matching_set[local] = dl_link
	elif local_time < feed_time:
		update_set[local] = dl_link
	elif feed_time < local_time:
		aof_set[local] = dl_link
	else:
		conflict_set[local] = dl_link

def write_file_from_dict(d, file_name):	
	with open(file_name, 'w') as f:
		for fn in d:
			f.write(d[fn]+ ';' +fn +'\n') 			

def get_dataset(link, params, base_url, base_folder):
	ns = '{http://www.w3.org/2005/Atom}' #namespace	
	s = add_params(link, params)	
	entry_feed = ET.ElementTree(file=urllib.urlopen(s)).getroot()	

	print "Feed URL:"
	print s
	print entry_feed.find(ns+'title').text
	
	dl_file = 'dl_list.txt'	
	dl_set = {}
	
	update_file = 'update_list.txt'	
	update_set = {}

	aof_file = 'ahead_of_feed_list.txt' #Ahead Of Feed	
	aof_set = {}

	conflict_file = 'conflict_list.txt' #matching timestamps, but different file sizes	
	conflict_set = {}

	removed_file = 'removed_list.txt'	
	removed_set = {}

	removed_file = 'matching_list.txt'	
	matching_set = {}

		
	for child in entry_feed.findall(ns+'entry'):
		dl_link = child.find(ns+'link').get('href')		
		path,slash, f = dl_link.split('?')[0][len(base_url):].rpartition(r'/')
		path = base_folder + '/' + path		
		filename = path + slash + f				 		
		if not os.path.exists(path):
			os.makedirs(path)
	
		if not os.path.exists(filename):				
			dl_set[filename] = dl_link
		elif os.path.isdir(filename):
			print 'Trying to overwrite folder with file. Something is definately wrong here...'
		else:
			check_newer(filename, dl_link, update_set, aof_set, conflict_set, matching_set)
	
	check_local_files(base_folder, [update_set, aof_set, conflict_set, dl_set, matching_set], removed_set)	
	write_file_from_dict(dl_set,dl_file)
	write_file_from_dict(update_set,update_file)
	write_file_from_dict(aof_set,aof_file)
	write_file_from_dict(conflict_set,conflict_file)
	write_file_from_dict(removed_set,removed_file)


	print_report(['new files to be downloaded', 'files to be updated', 'files with newer local versions', 'files with matching timestamps, but conflicting sizes', 'files not found in feed', 'files matching those in feed'], [dl_set, update_set, aof_set, conflict_set, removed_set, matching_set])	
	


#get_dataset('https://tiedostopalvelu.maanmittauslaitos.fi/tp/feed/mtp/laser/etrs-tm35fin-n2000',['api_key=bg5gt3qcn0gkv04rbukeam1btb', 'updated=2017-03-27T00:00'],'https://tiedostopalvelu.maanmittauslaitos.fi/tp/tilauslataus/tuotteet/', 'mml', 3)


get_dataset('http://wwwd3.ymparisto.fi/d3/atom/luonnonsuojelualueet.xml',None,'http://wwwd3.ymparisto.fi/d3/', 'syke')


print "\nAll Done"

