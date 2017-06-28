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
		for link in child.findall(ns+'link'):
			print link.get('href')
		continue	
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


def main():
	
	args = parse_args()
	feed_files ={}
	get_dataset(args.feed_url,args.p, args.b, args.base_directory, feed_files)

	
	

if __name__ == "__main__":
    main()	


