
import xml.dom.minidom
import xml.parsers.expat
import re
import pdb
from enum import Enum
import codecs
import logging
from  DictStemmer import DictStemmer

class SynonyAnalyzer():	
	class parseALine():
		
		posMap = {"adjective":'j', 'verb active':'v', 'verb neuter':'v', 'noun':'n', 'preposition':'i', "adverb":'r',
		'a':'j', 'adj':'j', 'vt':'v', 'vi':'v', 'adv':'r', 'n':'n', 'prep':'i','conj':'c', 'v':'v', 'num':'n', 'interj':'c'
			}
			
		refer = {"I" : 1, "II" : 2, "III" : 3, "IV" : 4, "V" : 5, "VI" : 6, "VII" : 7, "VIII" : 8, "IX" : 9, "X" : 10, 
         "XI" : 11, "XII" : 12, "XIII" : 13, "XIV" : 14, "XV" : 15, "XVI" : 16, "XVII" : 17, "XVIII" : 18, "XIX" : 19, "XX" : 20, 
         "XXI" : 21, "XXII" : 22, "XXIII" : 23, "XXIV" : 24 }
         	
		def __init__(self, node, word, analyzer):
			self.result = ''
			self.analyzer = analyzer
			self.word = word
			self.docNode = node
			self._isLineHead = True
			#self._lastLineStatus = LastLineStatus.EMPTY
			self._curPos = ''
			self._curIdx = 1
			self._lineBuffer = ''
			self.parseChild(self.docNode)
			re.sub(r'\n+', '\n', self.result)

	
		def parseChild(self, node):
			if (node.nodeType == xml.dom.Node.TEXT_NODE and re.sub(r'\s+', '', node.nodeValue) != "" ):
				if (self._isLineHead == True):
					self.result += "[" + self._curPos + " " + str(self._curIdx) + "]" + node.nodeValue
				else:
					self.result += node.nodeValue
				self._isLineHead = False
				#if (self._curPos != ''):
				#	self.analyzer.setupMapping(self.word, self._curPos, self._curIdx, node.nodeValue)
				self._lineBuffer += node.nodeValue
				#self._lastLineStatus = LastLineStatus.NORMAL
			elif (node.nodeType == xml.dom.Node.ELEMENT_NODE):
				if (node.nodeName == 'br'):
					if (self._lineBuffer != '') and (self._curPos != ''):
						self._lineBuffer = re.sub(r'\[[\w .,]+\] | \([\w .,]+\)', '', self._lineBuffer, flags=re.X)
						self.analyzer.setupMapping(self.word, self._curPos, self._curIdx, self._lineBuffer)
					self._lineBuffer = ''
					self.result += '\n'
					self._isLineHead = True
					self._curIdx += 1
					#self._lastLineStatus = LastLineStatus.EMPTY
					return
				elif (node.nodeName == 'span'):
					classAttr = node.getAttribute('class')
					if (classAttr == 'xdxf_k'):
						#self.word = node.nodeValue
						pass
					elif (classAttr == 'xdxf_ex_old'):
						return
				if (self._isLineHead == True and len(node.childNodes) == 1 and node.firstChild.nodeType == xml.dom.Node.TEXT_NODE):
					txtChild = node.firstChild.nodeValue
					m = re.match(r'^(adj|adv|vt|vi|v|n|prep|conj|a|num|interj)\.$', txtChild)
					if (m == None):
						m = re.match(r"^(verb\ active | verb\ neuter | noun | adjective |  adverb |  preposition)$", txtChild, re.X)
					if (m != None):
						self._curPos = self.posMap[m.group(1)]
						self._curIdx += 1 # 如果显示的是 v_1 v_2 n_1 n_2这样按照词性+序号的话，就需要重置；如果显示的是v_1 v_2 n_3 n_4就不需要重置
						#self._isLineHead = False
						return
						#print("pos: [" + getInfo.posMap[self._curPos] + "]")
					else:
						m = re.match(r"^((?:[0-9]+) | (?:[IVXL]+))[\.]?\s*$", txtChild, re.X)
						if (m != None):
							#if m.group(1) in refer:
							#	self._curIdx = refer[m.group(1)]
							#else:
							#	self._curIdx = int(m.group(1))
							self._curIdx += 1
							#self._isLineHead = False
							return
							#print("IDX: [" + str(self._curIdx) + "]")
			for child in node.childNodes:
				self.parseChild(child)
			
			if (node.nodeName == 'dom'):
				#处理最后的一行，参考abase这个词条的XML
				if (self._lineBuffer != '') and (self._curPos != ''):
					self._lineBuffer = re.sub(r'\[[\w .,]+\] | \([\w .,]+\)', '', self._lineBuffer, flags=re.X)
					self.analyzer.setupMapping(self.word, self._curPos, self._curIdx, self._lineBuffer)


	def __init__(self, dictfile):
		self._dict = dictfile
		self.logger = logging.getLogger('synonymAnalizer')
		self._wordPos2WList = {}
		self._hashWordPos = {}
		self._hashWordPos2SetIdx = {}
		self._hashSetIdx2Set = {}
		self._idx2wordPos = {}
		self._combineHash = {}
		self._countSynonyEnclosure = {}
		self.synonyms = {}
		

	def updateHashMap(self, mapping, word, pos, idx, something):
		if (word not in mapping):
			mapping[word] = {}
		if pos not in mapping[word]:
			mapping[word][pos] = {}
		mapping[word][pos][idx] = something

	def setupMapping(self, word, pos, idx, wordlist):
		# this is called by parseALine
		if (word=='abase'):
			print('break here')
		if (word not in self._wordPos2WList):
			self._wordPos2WList[word] = {}
		if (pos not in self._wordPos2WList[word]):
			self._wordPos2WList[word][pos] = {}
		wordList = re.split(r'\s*[,\.;]+\s*', re.sub(r'^\s*[:,\.;]? | [:,\.;]*\s*$', '', wordlist.lower(), flags=re.X), flags=re.X)
		for w in wordList:
			if w == '':
				continue
			if (idx not in self._wordPos2WList[word][pos]):
				self._wordPos2WList[word][pos][idx] = set([w])
			else:
				self._wordPos2WList[word][pos][idx].add(w)

	def startUnion_v2(self, iterations = 2):
		curIdx = 0
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					curIdx += 1
					self._hashWordPos[word + '$' + pos + '#' + str(idx)] = curIdx
					self._idx2wordPos[curIdx] = word + '$' + pos + '#' + str(idx)
					#print("IDX[" + word + '$' + pos + '#' + str(idx) + "]" + str(curIdx-1))
		
		# 超过 此值的 index，则仅出现在词条释义中，但没有自己的释义； 或者就是，该词出现在某个词多条释义项中。
		maxWordPosIdx = curIdx
				
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					wordIdx1 = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
					#if word == 'lunge':
					#		print('break here')
					for synonym in self._wordPos2WList[word][pos][idx]:
						if synonym == word:
							continue
						if not re.match(r'\(?[\w ]+\)?', synonym):
							print('ATTENTION %s %s %d, %s correct format the Dictionary File' % (word, pos, idx, synonym))
						#if synonym=='':
						#	print('synonym NULL:  %s[%s %d]' % (word, pos, idx))
						if synonym in self._wordPos2WList and pos in self._wordPos2WList[synonym] and \
						    len(self._wordPos2WList[synonym][pos]) <= 3:
							wordIdx2 = matchCnt = 0
							for idxSynonym in self._wordPos2WList[synonym][pos]:
								if word in self._wordPos2WList[synonym][pos][idxSynonym]:
									wordIdx2 = self._hashWordPos[synonym + '$' + pos + '#' + str(idxSynonym)]
									matchCnt += 1
							if matchCnt == 1:
								self._hashSetIdx2Set[wordIdx1] = self._hashSetIdx2Set.get(wordIdx1, set()) | set([wordIdx2])
								self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (wordIdx2, word, pos, idx,
												", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
													))
							#elif matchCnt == 0 and len(self._wordPos2WList[synonym][pos]) == 1:
							#  # 这段代码，之所以注释掉，是因为研究了retaliate 包含 reciprocate，引入了equal不相关的词的缘故，所以保守起见，禁用
							#	wordIdx2 = self._hashWordPos[synonym + '$' + pos + '#' + str(idxSynonym)]
							#	self._hashSetIdx2Set[wordIdx1] = self._hashSetIdx2Set.get(wordIdx1, set()) | set([wordIdx2])
							#	self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (wordIdx2, word, pos, idx,
							#					", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
							#						))
							else:
								# word出现在  synonym 多条释义项中。
								# 或者 synonym 所有释义中，word 一次都没有出现
								if synonym + '$' + pos not in self._hashWordPos:
									curIdx += 1
									self._hashWordPos[synonym + '$' + pos] = curIdx
									self._idx2wordPos[curIdx] = synonym + '$' + pos
									#self._hashSetIdx2Set[curIdx] = set([curIdx])
								if wordIdx1 in self._hashSetIdx2Set:
									self._hashSetIdx2Set[wordIdx1].add(self._hashWordPos[synonym + '$' + pos])
									self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (self._hashWordPos[synonym + '$' + pos], word, pos, idx,
												", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
													))
								else:
									self._hashSetIdx2Set[wordIdx1] =  set([self._hashWordPos[synonym + '$' + pos]])
									self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (self._hashWordPos[synonym + '$' + pos], word, pos, idx,
												", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
													))
						else:
							# synonym 仅出现在word词条释义中，但synonym没有自己的词条
							if synonym not in self._hashWordPos:
								curIdx += 1
								self._hashWordPos[synonym] = curIdx
								self._idx2wordPos[curIdx] = synonym
								#self._hashSetIdx2Set[curIdx] = set([curIdx])
							if wordIdx1 in self._hashSetIdx2Set:
								self._hashSetIdx2Set[wordIdx1].add(self._hashWordPos[synonym])
								self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (self._hashWordPos[synonym], word, pos, idx,
												", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
													))
							else:
								self._hashSetIdx2Set[wordIdx1] =  set([self._hashWordPos[synonym]])
								self.logger.debug("+%d, SET[%s$%s#%d] = {%s}"% (self._hashWordPos[synonym], word, pos, idx,
												", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[wordIdx1]])
													))
				
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					wordIdx = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
					unionSet = self._hashSetIdx2Set[wordIdx].copy()
					itrCnt = iterations
					#self.logger.critical("before start, SET[%s$%s#%d] = {%s}"% (word, pos, idx,	", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in set([i for i in unionSet if i <= maxWordPosIdx])])))
					newlyIntroduced = set([i for i in unionSet if i <= maxWordPosIdx])
					beforeExpand = set([i for i in unionSet if i <= maxWordPosIdx])
					while (itrCnt > 0):
						for item in newlyIntroduced:
							newComers = self._hashSetIdx2Set[item] - unionSet
							unionSet |= self._hashSetIdx2Set[item]
							self.logger.debug("%s, Iteration %d, SET[%s$%s#%d], incorporate {%s}"% (self._idx2wordPos[item],itrCnt, word, pos, idx,
																", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in set([i for i in newComers if i <= maxWordPosIdx])])
													))
						self.logger.debug("Iteration %d, union SET[%s$%s#%d] = {%s}"% (itrCnt, word, pos, idx,
																			", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in set([i for i in unionSet if i <= maxWordPosIdx])])
																			))
						newlyIntroduced = set([i for i in unionSet if i <= maxWordPosIdx]) - beforeExpand
						beforeExpand = set([i for i in unionSet if i <= maxWordPosIdx])
						changed = len(newlyIntroduced)
						if not changed or len([i for i in unionSet if i <= maxWordPosIdx]) > 40:
							break
						itrCnt -= 1
					self.logger.debug("after union SET[%s$%s#%d] = {%s}"% (word, pos, idx,
																			", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in set([i for i in unionSet if i <= maxWordPosIdx])])
																			))
					synonymSet = set()
					for item in unionSet:
						mObj = re.match(r'^([^$]+)', self._idx2wordPos[item])
						if (mObj == None):
							print("mObj could not match")
						synonymSet.add(mObj.group(1))
					synonymSet.discard(word)
					self.updateHashMap(self.synonyms, word, pos, idx, synonymSet)


	def startUnion_v1(self):
		blacklist = [
		 # because it contains (a) which explain phrases meanings
		'stand', 'hold', 'advance', 'amount', 'associate', 'bear', 'block', 'check'
		            'chip', 'clutch', 'dispense', 'dispose', 'draw' , 'element', 'error', 'face',
		            'facility', 'flake', 'foul', 'impose', 'lace', 'lap',  'lay', 'lean', 'leasure', 'lot',
		            'mean', 'pack', 'pitch', 'polish', 'premium', 'press', 'prey', 'proceeding', 'pump', 'rag', 
		            'ready', 'reckon','rip', 'ripe', 'roll','rote','screw','sight','slack', 'snap','stack', 'stick',
		            'strike', 'string','subject', 'tap','tie', 'touch', 'vain', 'vengeance', 'violence', 'wade', 
		            'wrap', 'advance', 'amount', 'associate', 'bear', 'block', 'primary', 'control'
		            ]
		i = 1
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					self._hashWordPos[word + '$' + pos + '#' + str(idx)] = i
					self._idx2wordPos[i] = word + '$' + pos + '#' + str(idx)
					i += 1
					print("IDX[" + word + '$' + pos + '#' + str(idx) + "]" + str(i-1))
		
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					wordPosIdx = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
					self._hashWordPos2SetIdx[wordPosIdx] = wordPosIdx
					self._hashSetIdx2Set[wordPosIdx] = set([wordPosIdx])
					
		changed = False
		iterIdx = 0
		while True:
			iterIdx += 1
			for word in self._wordPos2WList:
				for pos in self._wordPos2WList[word]:
					for idx in self._wordPos2WList[word][pos]:
						wordIdx1 = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
						setIdx1 = self._hashWordPos2SetIdx[wordIdx1]
						topHalf = (self._hashSetIdx2Set[setIdx1] - set([wordIdx1]))
						bottomHalf = set()
						for synonym in self._wordPos2WList[word][pos][idx]:
							if synonym == word:
								continue
							if word in blacklist or synonym in blacklist:
								continue	
							if synonym in self._wordPos2WList and pos in self._wordPos2WList[synonym]:
								for idxSynonym in self._wordPos2WList[synonym][pos]:
									if word in self._wordPos2WList[synonym][pos][idxSynonym]:
										wordIdx2 = self._hashWordPos[synonym + '$' + pos + '#' + str(idxSynonym)]
										setIdx2 = self._hashWordPos2SetIdx[wordIdx2]
										bottomHalf |= (self._hashSetIdx2Set[setIdx2] - set([wordIdx2]))
										if (setIdx1 != setIdx2):
											changed = True
											newSet = self._hashSetIdx2Set[setIdx1] | self._hashSetIdx2Set[setIdx2]
											#self.logger.debug("SET_1[%s %d] = {%s}, \n\nSET_2[%s %d] = {%s}  \n\nSET_1 AND SET_2 = {%s}"% (self._idx2wordPos[wordIdx1], wordIdx1,
											#																															", ".join([self._idx2wordPos[m] + '(' + str(m) + ')' for m in self._hashSetIdx2Set[setIdx1]]), 
											#																														  self._idx2wordPos[wordIdx2], wordIdx2, 
											#																														  ", ".join([self._idx2wordPos[m] + '(' + str(m)  + ')' for m in self._hashSetIdx2Set[setIdx2]]),
											#																														  ", ".join([self._idx2wordPos[m] + '(' + str(m)  + ')' for m in self._hashSetIdx2Set[setIdx1] & self._hashSetIdx2Set[setIdx2]])
											#																														  ))
											self._hashWordPos2SetIdx[wordIdx1] = self._hashWordPos2SetIdx[wordIdx2] = setIdx1
											self._hashSetIdx2Set[setIdx1] = newSet
											for item in newSet:
												self._hashWordPos2SetIdx[item] = setIdx1
						for item in topHalf ^ bottomHalf:
							self._countSynonyEnclosure[item] = self._countSynonyEnclosure.get(item, 0) + 1
			if not changed:
				break
			else:
				changed = False
			print(iterIdx)
		
		for word in self._wordPos2WList:
			for pos in self._wordPos2WList[word]:
				for idx in self._wordPos2WList[word][pos]:
					wordIdx = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
					setIdx = self._hashWordPos2SetIdx[wordIdx]
					if (word == 'smother' and idx == 14):
						print('break here')
					synonymSet = set()
					for wordPosIdx in self._hashSetIdx2Set[setIdx]:
						mObj = re.match(r'^(.+)\$(.+)#(.+)$', self._idx2wordPos[wordPosIdx])
						if (mObj == None):
							print(1)
						wordX = mObj.group(1)
						posX = mObj.group(2)
						idxX = int(mObj.group(3))
						synonymSet |= (self._wordPos2WList[wordX][posX][idxX] | set([wordX]))
						#synonymSet |= self._wordPos2WList[wordX][posX][idxX]
					self.synonyms[word] = {}
					self.synonyms[word][pos] = {}
					self.synonyms[word][pos][idx] = synonymSet - set([word])

	def startParse(self):
		print("Starting analyzeing Synonyms: %s" % self._dict)
		try:
			#fdw = open('.\log222.txt', mode = 'wt')
			fdi = open(self._dict, mode = 'rt', encoding='utf_8_sig') 
			#fdi = open(self._dict, mode = 'rt')
		except OSError:
			print("file can't be opened\n");
			#fdw.close()
			fdi.close()
			return
		while (1):
			firstLine = fdi.readline()
			#print("reading %s " % firstLine)
			#if firstLine[:3] == codecs.BOM_UTF8:
			#	firstLine = firstLine[len(codecs.BOM_UTF8):]
			secondLine = fdi.readline()
			thirdLine = fdi.readline()
			if (firstLine == ''):
				break
			strParse=re.sub(r'<([Bb][Rr])>', r'<br/>', secondLine)
			strParse=re.sub(r'&nbsp;', r'', strParse)
			strParse=re.sub(r'&quot;', r'', strParse)
			strParse=re.sub(r'>\s+<', '><', strParse)
			strParse=re.sub(r'<i>See</i>', '', strParse)
			strParse=re.sub(r'\(<i>[\w \.\']+</i>\.?\)', '', strParse)
			strParse=re.sub(r'\[<i>[\w \.]+</i>\.?\]', '', strParse)
			strParse=re.sub(r'\(<i>also</i><b>\w+</b>\)</b>', '', strParse)
			strParse=re.sub(r'\[Fr\.\]', '', strParse)
			strParse=re.sub(r'See (<a class="xdxf_kref")', r'\1', strParse)
			strParse=re.sub(r'<span style="color:blue">Colloq</span>', '', strParse)
			strParse=re.sub(r'<span class="xdxf_abbr">[^<>]*</span>', '', strParse)
			strParse=re.sub(r'<span style="color:blue">[a-zA-Z\ ]+</span>', '', strParse)
			strParse=re.sub(r',-', ',', strParse)
			strParse='<dom>' + strParse + '</dom>'
			try:
				word = re.match(r'^(.+)$', firstLine).group(1)
				markObj = SynonyAnalyzer.parseALine(xml.dom.minidom.parseString(strParse), word, self)
			except xml.parsers.expat.ExpatError:
				#strParse = re.sub(r'\(<i>also</i><b>\w+</b>\)</b>', '', strParse)
				try:
					markObj = SynonyAnalyzer.parseALine(xml.dom.minidom.parseString(strParse), word, self)
				except xml.parsers.expat.ExpatError:
					print("ExaptError:%s" % firstLine)
			self.logger.debug(firstLine)
			self.logger.debug(markObj.result + '\n\n')
		

		ITERATIONS = 3
		self.startUnion_v2(ITERATIONS)
		
		self.logger.critical('========== Synonymous Output (Iterate %d times) =================' % ITERATIONS)
		for word in sorted(self._wordPos2WList):
			for pos in sorted(self._wordPos2WList[word]):
				for idx in sorted(self._wordPos2WList[word][pos]):
					wordIdx = self._hashWordPos[word + '$' + pos + '#' + str(idx)]
					self.logger.critical("%s: %s" % (self._idx2wordPos[wordIdx], ', '.join(self.synonyms[word][pos][idx])))
		#fdw.close()				
		fdi.close()
		return self


def getSynonyms(wordPos, symSet1, symSet2, wordPosInterested):
	word, pos = re.split(r"[$]", wordPos)
	result = ''
	if word in symSet1:
		if pos in symSet1[word]:
			cnt = 1
			for idx in symSet1[word][pos]:
				wordPosSet = set([w + '$' + pos for w in symSet1[word][pos][idx]])
				wordPosFirst = wordPosSet & wordPosInterested
				wordPosSecond = wordPosSet - wordPosFirst
				sortSet1 = [re.split(r"[$]", m)[0] for m in sorted(wordPosFirst)]
				sortSet2 = [re.split(r"[$]", m)[0] for m in sorted(wordPosSecond)]
				result += 'SymSet_1 %d[%s]\n' % (cnt, ", ".join(sortSet1) + ' ●' + ", ".join(sortSet2))
				cnt += 1
	
	if word in symSet2:
		if pos in symSet2[word]:
			cnt = 1
			for idx in symSet2[word][pos]:
				wordPosSet = set([w + '$' + pos for w in symSet2[word][pos][idx]])
				wordPosFirst = wordPosSet & wordPosInterested
				wordPosSecond = wordPosSet - wordPosFirst
				sortSet1 = [re.split(r"[$]", m)[0] for m in sorted(wordPosFirst)]
				sortSet2 = [re.split(r"[$]", m)[0] for m in sorted(wordPosSecond)]
				result += 'SymSet_2 %d[%s]\n' % (cnt, ", ".join(sortSet1) + ' ●' + ", ".join(sortSet2))
				cnt += 1
	return result	


if __name__ == "__main__":
	
	GreRedBookAlphabetOrder=[   ''      , 'affordable', 'aorta'      ,   'attenuate', 'bewilder', 'cabal', 
	                'chaste'  , 'commodious', 'construe'   , 'cumbersome' , 'dent'    , 'discretion',
	                'droplet' , 'enmity'    , 'exhilarate' , 'figment'    , 'frustrate', 'grain',
	                'hemostat', 'impalpable', 'ineluctable', 'interplay'  , 'lampoon'  , 'macabre',
	            'metropolitan', 'nadir'     , 'ogle'       , 'paramount'  , 'phenomena', 'precocious',
	            'provocation' , 'recall'    , 'resigned'   , 'sapphire'   , 'shrewd'   , 'sparse'    ,
	            'stroke'      , 'tamp'      , 'transcend'  , 'unrepentant', 'vindicate', 'zzzzzzzzzzz'   ]
	            
	stemmer = DictStemmer()
	logging.basicConfig(format='%(message)s',  filename="./SynonymLog.txt", filemode='w', level=logging.DEBUG)
	pdb.set_trace() 
	symSet1 = SynonyAnalyzer("./DUMP Oxford Synonyms.txt").startParse()
	symSet2 = SynonyAnalyzer("./DUMP Soule's Dictionary of English Synonyms.txt").startParse()

	wordPosInterested = set(wordPos for wordPos in stemmer.wordsInfo if re.search("G|T|K", stemmer.wordsInfo[wordPos]))
	sortWordPosList = sorted([wordPos for wordPos in wordPosInterested if re.search("G", stemmer.wordsInfo[wordPos])])
	for i in range(1,42):
		logging.critical("------------- Test: GRE RedBook List " + str(i) + " Exercise-----------------")
		chapWordPos = [wp for wp in sortWordPosList if re.split(r"[$]", wp)[0].lower() < GreRedBookAlphabetOrder[i] and re.split(r"[$]", wp)[0] >= GreRedBookAlphabetOrder[i-1]]
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in chapWordPos)
		for wordPos in sorted(chapWordPos):
			word, Pos = re.split(r"[$]", wordPos)
			testWord = re.sub(r'(?!^)[AEIOUaeiou]+?(?!$)', "_", word)
			logging.critical("%-" + str(maxWordLen+3) + "s%2s  %s%s", testWord, Pos, stemmer.WordsMeaning[wordPos], '★ '+word)
			logging.critical("%s" % getSynonyms(wordPos, symSet1.synonyms, symSet2.synonyms, wordPosInterested, ))
	
	sortWordPosList = [wordPos for wordPos in wordPosInterested if re.search("K", stemmer.wordsInfo[wordPos])]
	for i in range(1, 44):
		logging.critical("------------- Test: GRE GreenBook List " + str(i) + " Exercise-----------------")
		chapWordPos = [wordPos for wordPos in sortWordPosList if stemmer.GreenBookWord2ChapId[re.split(r"[$]", wordPos)[0]] == i ]
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in chapWordPos)
		for wordPos in sorted(chapWordPos):
			word, Pos = re.split(r"[$]", wordPos)
			testWord = re.sub(r'(?!^)[AEIOUaeiou]+?(?!$)', "_", word)
			logging.critical("%-" + str(maxWordLen+3) + "s%2s  %s%s", testWord, Pos,  stemmer.WordsMeaning[wordPos], '★ '+word)
			logging.critical("%s" % getSynonyms(wordPos, symSet1.synonyms, symSet2.synonyms, wordPosInterested, ))


