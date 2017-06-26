import xml.etree.ElementTree as ET
import os
import sys
import urllib
from subprocess import call
from sets import Set
from datetime import datetime, timedelta
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

def check_local_files(rootdir, local_files):
	for subdir, dirs, files in os.walk(rootdir):
		if os.path.exists(os.path.join(subdir, '.atom_ignore_extracted_folder.txt')):
			continue
		for file in files:
			fn = os.path.join(subdir, file)
			local_files[fn] = [None, None]
			update_local_time_and_size(fn,local_files[fn])
						
def print_set(header, st):
	print ''
	print str(len(st))+' '+ header
	for f in st:
		print '	', f, st[f][0],st[f][1]	


def write_report(feed_files, local_files, report_file):
	with open(report_file, 'w') as report:
		for f in feed_files:
			if f in local_files:
				delta = feed_files[f][0]-local_files[f][0]			
				if delta >timedelta(hours=24):
					report.write( 'update; ' + f+';' +  str(feed_files[f][0]) + ';'+str(feed_files[f][1])+';'+str(local_files[f][0])+';'+str(local_files[f][1]) +'\n')
				elif delta <timedelta(hours=-24):
					report.write( 'aof; ' + f +';'  str(feed_files[f][0]) + ';'+str(feed_files[f][1])+';'+str(local_files[f][0])+';'+str(local_files[f][1])+'\n')
				else:
					report.write('ok; ' +f+';' +  str(feed_files[f][0]) + ';'+str(feed_files[f][1])+';'+str(local_files[f][0])+';'+str(local_files[f][1])+'\n')
				
			else:
				report.write( 'dl; ' + f+'\n')
				#ladataan
		for f in local_files:
			if f not in feed_files:
				report.write('removed; '+f+'\n')



def download_set(a_set):
	for link in a_set:
		path,slash, f = link.rpartition(r'/')
		if not os.path.isdir(path):
			os.makedirs(path)
		call(['wget', '-O', link,a_set[link][3]]) 

def update_local_time_and_size(local, meta):
	if os.path.exists(local):
		mtime = os.path.getmtime(local)
		meta[0] = datetime.utcfromtimestamp(mtime)
		meta[1] = os.path.getsize(local)	


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
def dtparse(t):
	ret = datetime.strptime(t[0:19],'%Y-%m-%dT%H:%M:%S')
	if t[-6]=='+':
		ret-=timedelta(hours=int(t[-5:-3]),minutes=int(t[-2:]))
	elif t[-2]=='-':
		ret+=timedelta(hours=int(t[-5:-3]),minutes=int(t[-2:]))
	
	return ret

def get_dataset(link, params, base_url, base_folder,files):
	if not base_url:
		base_url = 'http://'
	ns = '{http://www.w3.org/2005/Atom}' #namespace	
	s = add_params(link, params)	
	
	et = None
	try:
		et = ET.parse(urllib.urlopen(s))
	except ET.ParseError as detail:
		print detail
    		return None

	entry_feed = et.getroot()
	print "Feed URL:"
	print s
	print entry_feed.find(ns+'title').text

	
	next = entry_feed.findall(ns+"link[@rel='next']")
	if next:
		next_link = next[0].get('href')			
		get_dataset(next_link, None,  base_url, base_folder, files)
	
	for child in entry_feed.findall(ns+'entry'):
		link=child.find(ns+'link')		
		dl_link = link.get('href')		
		path,slash, f = dl_link.split('?')[0][len(base_url):].rpartition(r'/')		
		path = base_folder  + path		
		filename = path + slash + f
				
		meta = [dtparse(child.find(ns+'updated').text) ,link.get('length'),dl_link]
		files[filename] = meta

	


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('feed_url', help='URL of the dataset xml file')
	parser.add_argument('-b', help='URL to the base of the structure to be downloaded, file structure will be copied after this', metavar='url')
	parser.add_argument('base_directory', help='local directory where files should be downloaded')
	parser.add_argument('-d', help='download new datasets',action="store_true")
	parser.add_argument('-u', help='update datasets with newer versions in feed',action="store_true")
	parser.add_argument('-p', nargs = '*', help='parameters to be added to feed url', metavar='params')
	parser.add_argument('-r', help='write report to file',metavar="local_file")
	return parser.parse_args()

def unzip_set(a_set):
	for fn in a_set:
		filename, ext = os.path.splitext(fn)			
		if ext == '.zip':
			call(['unzip','-o', fn,'-d', filename ])
			call(['touch', os.path.join(filename, '.atom_ignore_extracted_folder.txt')])

def main():
	
	args = parse_args()
	feed_files ={}
	local_files ={}
	get_dataset(args.feed_url,args.p, args.b, args.base_directory, feed_files)
	check_local_files(args.base_directory, local_files)
	write_report(feed_files, local_files, args.r)
	
	

if __name__ == "__main__":
    main()	







