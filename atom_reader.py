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
				removed_set[fn] = [None, None,None,None,None]
				update_local_time_and_size(fn,removed_set[fn])
						
def print_set(header, st):
	print ''
	print str(len(st))+' '+ header
	for f in st:
		print '	', f, st[f][1],st[f][2],st[f][3],st[f][4]	


def print_report(headers, sets):
	for st, hd in zip(sets, headers):
		print_set(hd,st)



def download_set(a_set):
	for link in a_set:
		call(['wget', '-O', link,a_set[link][0]]) 

def update_local_time_and_size(local, meta):
	if os.path.exists(local):
		mtime = os.path.getmtime(local)
		meta[1] = datetime.utcfromtimestamp(mtime)
		meta[3] = os.path.getsize(local)	


def update_time_and_size(local, meta):
	update_local_time_and_size(local, meta)
	
	url_meta = urllib.urlopen(meta[0]).info()
	feed_time = datetime.strptime(url_meta.getheader('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z')
	feed_size = int(url_meta.getheader('Content-Length'))
	meta[2]=feed_time
	meta[4]=feed_size

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
	
	dl_set = {}
	update_set = {}
	aof_set = {}
	conflict_set = {}
	removed_set = {}
	matching_set = {}

		
	for child in entry_feed.findall(ns+'entry'):
		dl_link = child.find(ns+'link').get('href')		
		path,slash, f = dl_link.split('?')[0][len(base_url):].rpartition(r'/')
		path = base_folder + '/' + path		
		filename = path + slash + f

		meta = [dl_link,None,None,None,None]
		update_time_and_size(filename, meta)
			 		
		if not os.path.exists(path):
			os.makedirs(path)		
		if not os.path.exists(filename):				
			dl_set[filename] = meta
		elif os.path.isdir(filename):
			print 'Trying to overwrite a folder with a file. Something is probably wrong here.'
		else:

			if meta[1] == meta[2] and meta[3] == meta[4]:
				matching_set[filename] = meta
			elif meta[1] < meta[2]:
				update_set[filename] = meta
			elif meta[1] > meta[2]:
				aof_set[filename] = meta
			else:
				conflict_set[filename] = meta
	
	check_local_files(base_folder, [update_set, aof_set, conflict_set, dl_set, matching_set], removed_set)	

	return dl_set, update_set, aof_set, conflict_set, removed_set, matching_set


def write_sets_to_files(dl_set, update_set, aof_set, conflict_set, removed_set, matching_set):
	dl_file = 'dl_list.txt'	
	update_file = 'update_list.txt'	
	aof_file = 'ahead_of_feed_list.txt' #Ahead Of Feed	
	conflict_file = 'conflict_list.txt' #matching timestamps, but different file sizes
	removed_file = 'removed_list.txt'	
	matching_file = 'matching_list.txt'	
	

	write_file_from_dict(dl_set,dl_file)
	write_file_from_dict(update_set,update_file)
	write_file_from_dict(aof_set,aof_file)
	write_file_from_dict(conflict_set,conflict_file)
	write_file_from_dict(removed_set,removed_file)
	
	

sets = get_dataset('http://wwwd3.ymparisto.fi/d3/atom/luonnonsuojelualueet.xml',None,'http://wwwd3.ymparisto.fi/d3/', 'syke')
print_report(['new files to be downloaded', 'files to be updated', 'files with newer local versions', 'files with matching timestamps, but conflicting sizes', 'files not found in feed', 'files matching those in feed'], sets)	

download_set(sets[0])


#get_dataset('https://tiedostopalvelu.maanmittauslaitos.fi/tp/feed/mtp/laser/etrs-tm35fin-n2000',['api_key=bg5gt3qcn0gkv04rbukeam1btb', 'updated=2017-03-27T00:00'],'https://tiedostopalvelu.maanmittauslaitos.fi/tp/tilauslataus/tuotteet/', 'mml', 3)



print "\nAll Done"



