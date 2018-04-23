from urllib import request
from datetime import datetime
from html.parser import HTMLParser
import re
import codecs
import yaml
import logging
import logging.config


class ContentParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.result = ''
		self.record = False
		self.cntP = 0
	
	def handle_data(self, data):
		if self.record:
			self.result += data
	
	def handle_starttag(self, tag, attributes):
		if tag == 'p':
			for name, value in attributes:
				if name == 'class' and value == 'cnnBodyText':
					self.cntP += 1
			if self.cntP == 3:
				self.record = True
		if tag == 'br':
			if self.record:
				self.result += '\n'

	def handle_endtag(self, tag):
		if self.record == True:
			if tag == 'p':
				self.record = False

class LinkParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.content = {}

	def handle_starttag(self, tag, attributes):
		if tag == 'a':
			for name, value in attributes:
				if (name == 'href'):
					objM = re.match(r'/TRANSCRIPTS/(\d\d)(\d\d)/(\d\d)/sn.*\.html', value)
					if not objM:
						continue
					year = objM.group(1)
					month = objM.group(2)
					day = objM.group(3)
					url = 'http://transcripts.cnn.com' + objM.group(0)
					dateInt = int( datetime.strptime(year + month + day, '%y%m%d').strftime('%Y%m%d') )
					logging.info('retrieving %d, url %s' % (dateInt, url))
					f = request.urlopen(url)
					p = ContentParser()
					p.feed(f.read().decode(encoding="utf-8"))
					if not re.search(r'END\s*\Z', p.result, re.M):
						raise Exception()
					self.content[dateInt] = p.result

with codecs.open(".\\ConfigureLogger.yml", 'r', 'utf-8') as f:
	D=yaml.load(f)
	logging.config.dictConfig(D)

f=request.urlopen('http://transcripts.cnn.com/TRANSCRIPTS/sn.html')
p = LinkParser()
p.feed(f.read().decode(encoding="utf-8"))

for i in sorted(p.content.keys(), reverse=True):
	logging.getLogger('CNNText').critical("Chapter %d.\n%s\n" % (i, p.content[i]))
	

