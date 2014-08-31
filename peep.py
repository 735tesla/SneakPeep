#!/usr/bin/python
#coding utf-8
from requests import get
from urllib import quote
from sys import argv
from multiprocessing import Pool
import webbrowser
import os
import unicodedata
from lockfile import FileLock
import re

glbl_port = None

def dl_pg(ip, timeout=1):
	try:
		url = 'http://'+ip+':'+str(glbl_port)
		print "[*] Downloading html page from: "+url
		url_attr_regex = "((?<=src=[\"'])|(?<=href=.))(?!(http(s|)(:|%3[Aa])))([0-9A-Za-z%?&#_=+./~])*(?=['\"])"
		data = unicodedata.normalize('NFKD', get(url, timeout=timeout).text).encode('ascii','ignore')
		data = re.sub(r'[^\x00-\x7F]+', '', data)
		data = re.sub(url_attr_regex, lambda mtch: ( (url+mtch.group()) if mtch.group().startswith('/') else (url+'/'+mtch.group()) ), data )
		return data
	except Exception,e:
		return '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><h1>Failed to retrieve page (%s).</h1></body></html>' % str(e)

def html2iframe(html):
	ret = '<iframe width="800" height="600" src="data:text/html;charset=utf-8,%s"></iframe>\n' % quote(html)
	return ret

def append_entry(ip):
	src = dl_pg(ip)
	lock = FileLock("output.html")
	lock.acquire()
	with open("output.html", 'a') as f:
		f.write('<h5>%s</h5><br>\n' % ip)
		f.write(html2iframe(src)+'<br>')
	lock.release()

def gen_report(ip_list, num_procs=50):
	with open('output.html', 'w') as f:
		f.write('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>\n')
	pool = Pool(num_procs)
	pool.map(append_entry, ip_list)
	with open('output.html', 'a') as f:
		f.write('</body></html>')


def main(args):
	if len(args)!=4:
		print "Usage: %s [list of hosts] [port] [number of concurrent tasks]" % args[0]
		return 1
	global glbl_port
	glbl_port = int(args[2])
	ip_list = []
	with open(args[1], 'r') as f:
		ip_list = f.read().split('\n')
	gen_report(ip_list, num_procs=int(args[3]))
	webbrowser.open_new_tab('file:///'+os.path.abspath('output.html'))
	return 0

if __name__ == '__main__':
	main(argv)
