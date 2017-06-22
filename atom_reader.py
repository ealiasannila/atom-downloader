import xml.etree.ElementTree as ET
import os
import sys
import urllib
from subprocess import call
from sets import Set
from datetime import datetime
import argparse


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
		if os.path.exists(os.path.join(subdir, '.atom_ignore_extracted_folder.txt')):
			continue
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
		print link
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
		f.write('local_file;download_link;local_modified_time;feed_modified_time; local_file_size;feed_file_size\n')
		for fn in d:
			f.write(fn+';')
			for col in d[fn]:
				f.write(str(col) + ';')
			f.write('\n') 			

def get_dataset(link, params, base_url, base_folder):
	if not base_url:
		base_url = 'http://'
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


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('feed_url', help='URL of the dataset xml file')
	parser.add_argument('-b', help='URL to the base of the structure to be downloaded, file structure will be copied after this', metavar='url')
	parser.add_argument('base_directory', help='local directory where files should be downloaded')
	parser.add_argument('-d', help='download new datasets',action="store_true")
	parser.add_argument('-u', help='update datasets with newer versions in feed',action="store_true")
	parser.add_argument('-p', nargs = '*', help='parameters to be added to feed url', metavar='params')
	parser.add_argument('-wd', help='write list of files to be downloaded',metavar="local_file")
	parser.add_argument('-wu', help='write list of files to be updated',metavar="local_file")
	parser.add_argument('-wa', help='write list of files with newer local versions than those in feed',metavar="local_file")
	parser.add_argument('-wc', help='write list of files with matching modified times but different sizes',metavar="local_file")
	parser.add_argument('-wr', help='write list of files not found in feed',metavar="local_file")
	parser.add_argument('-wm', help='write list of files matching locally and in feed',metavar="local_file")
	parser.add_argument('-uzd', help='unzip downloaded zip files (replaces existing files)', action='store_true')	
	parser.add_argument('-uzu', help='unzip updated zip files (replaces existing files)', action='store_true')	
	return parser.parse_args()

def unzip_set(a_set):
	for fn in a_set:
		filename, ext = os.path.splitext(fn)			
		if ext == '.zip':
			call(['unzip','-o', fn,'-d', filename ])
			call(['touch', os.path.join(filename, '.atom_ignore_extracted_folder.txt')])

def main():
	args = parse_args()
	sets = get_dataset(args.feed_url,args.p, args.b, args.base_directory)

	
	print_report(['new files to be downloaded', 'files to be updated', 'files with newer local versions', 'files with matching timestamps, but conflicting sizes', 'files not found in feed', 'files matching those in feed'], sets)	

	if args.d:	
		download_set(sets[0])
	if args.u:	
		download_set(sets[1])
	if args.wd:
		write_file_from_dict(sets[0], args.wd)
	if args.wu:
		write_file_from_dict(sets[1], args.wu)
	if args.wa:
		write_file_from_dict(sets[2], args.wa)
	if args.wc:
		write_file_from_dict(sets[3], args.wc)
	if args.wr:
		write_file_from_dict(sets[4], args.wr)
	if args.wm:
		write_file_from_dict(sets[5], args.wm)
	
	if args.uzd:
		unzip_set(sets[0])
	if args.uzu:
		unzip_set(sets[1])
	

if __name__ == "__main__":
    main()	



#get_dataset('https://tiedostopalvelu.maanmittauslaitos.fi/tp/feed/mtp/laser/etrs-tm35fin-n2000',['api_key=bg5gt3qcn0gkv04rbukeam1btb', 'updated=2017-03-27T00:00'],'https://tiedostopalvelu.maanmittauslaitos.fi/tp/tilauslataus/tuotteet/', 'mml', 3)





