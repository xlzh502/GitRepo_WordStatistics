# coding=gbk
from _thread import allocate_lock
import re
from string import Template
import logging

class NoWordInDict(ValueError):
	"The word is not in Dict"

class COCAPosInfoNotExist(ValueError):
	"The word's POS is not handled"

class SkipThisWord(ValueError):
	"Don't handle this word"


class DictStemmer(object):
	''' 
	DictStemmer :  Using dictionary file, so as to
	map a word to its main word
	'''
	
	singleton = {}
	L = allocate_lock()
	__initialized = 0
	
	
	__DictFile="2+2lemma.txt"
	__COCAFile="COCA 60000 Words Freq.txt"
	__GRE="gre words.txt"
	__Tofel="tofel words.txt"

	wordR = r"[a-zA-Z\-]+"
	spaceR = r"\s+"
	wordListR = Template(r'''$wordR(?:[,] $wordR)*''').substitute(locals())
	correspR = Template(r'''($wordR)[+]? -> \[($wordListR)\]''').substitute(locals())
	firstLineR = Template(r'''^$correspR|$wordR[+]?$$''').substitute(locals())
	secondLineR = Template(r'''\s+($correspR|$wordR)(?:[,] ($correspR|$wordR))*''').substitute(locals())
	secondLineElemR = Template(r'''($correspR|$wordR)''').substitute(locals())
	
	digitR=r"[0-9]+"
	posR=r"j|r|n|v|c|p|i|d"
	lQuoteR=r"\("
	rQuoteR=r"\)"
	dashR=r"-"
	CocaLineR = Template(r'''^$spaceR($digitR)$spaceR$lQuoteR?($wordR(?:$dashR$wordR|$dashR)*)$rQuoteR?$spaceR($posR)$$''').substitute(locals())
	
	GrePosR=r"(?:adj|adv|vt|vi|v|n|prep|conj|a)[\.]?"
	GrePosDescR=Template(r'''$GrePosR(?:[/]$GrePosR)*''').substitute(locals())
	GreChineseR=r"(?:[^a-zA-Z\.]+)"
	Gre1stLineR=Template(r'''$wordR$$''').substitute(locals())
	Gre2ndLineR=Template(r'''($GrePosDescR)($GreChineseR)''').substitute(locals())
	
	TofelPosR=r"(?:adj|adv|vt|vi|v|n|prep|conj)[\.]?"
	TofelPosDescR=Template(r'''$TofelPosR(?:[/]$TofelPosR)*''').substitute(locals())
	Tofel1stLineR=Template(r'''($digitR)$spaceR($wordR)$spaceR($TofelPosDescR)$spaceR([^a-zA-Z]+)''').substitute(locals())
	Tofel2ndLineR=Template(r'''($digitR)$spaceR($TofelPosDescR)$spaceR([^a-zA-Z]+)''').substitute(locals())
	
	LongPos2CocaPos = {'a':'j', 'adj':'j', 'vt':'v', 'vi':'v', 'adv':'r', 'n':'n', 'prep':'i','conj':'c', 'v':'v'}
	
	def __new__(cls, *args, **dw):
		DictStemmer.L.acquire_lock()
		if (cls.__name__  in cls.singleton):
			DictStemmer.L.release()
			return cls.singleton[cls.__name__]
		else:
			cls.singleton[cls.__name__] = super(DictStemmer, cls).__new__(cls,*args, **dw)
			return cls.singleton[cls.__name__]
	
	def __init__(self, *args, **dwgs):
		if (self.__class__.__initialized == 0):
			self.__class__.__initialized = 1
			super(DictStemmer, self).__init__()
			self.__doInit()
			DictStemmer.L.release()

	def __doInit(self):
		self.cocaDict = {}
		self.cocaMainWord = {}
		self.wordsInfo = {}
		self.cocaWordsInfo = {}
		self.cocaWordsFreq = {}
		self.WordsMeaning = {}
		
		self.__readDictFile()
		self.__readCOCA()
		self.__readGre()
		self.__readTofel()
	
	def __DictFile_handleWordList(self, mainWord, wordList):
		words = re.findall(DictStemmer.wordR, wordList)
		for word in words:
			self.cocaMainWord[word] = ""
			
	
	def __DictFile_1stLine(self, line):
		matchCorrespR = re.match(DictStemmer.correspR, line)
		matchWordR = re.match(DictStemmer.wordR, line)
		if (matchCorrespR):
			curWord = matchCorrespR.group(1);
			self.__DictFile_handleWordList(curWord, matchCorrespR.group(2))
		elif (matchWordR):
			curWord = matchWordR.group(0)
		else:
			assert(0)
		self.cocaMainWord[curWord] = ""
		return curWord
	
	
	def __DictFile_2ndLine(self, line, mainWord):
		elems = re.findall(DictStemmer.secondLineElemR, line)
		for elem in elems:
			if (re.match(DictStemmer.correspR, elem[0])):
				curWord = elem[1]
				wordList = elem[2]
				self.cocaDict[curWord] = mainWord
			elif (re.match(DictStemmer.wordR, elem[0])):
				curWord = elem[0]
				self.cocaDict[curWord] = mainWord
			else:
				assert(0)
		
	
	def __readDictFile(self):
		f = open(DictStemmer.__DictFile, "r")
		curWord = None

		for line in f:
			if (re.match(DictStemmer.firstLineR, line)):
				currWord = self.__DictFile_1stLine(line)
			elif (re.match(DictStemmer.secondLineR, line)):
				self.__DictFile_2ndLine(line, currWord)
			else:
				logging.warning("DICT line is not recognizable: %s" % line)
				assert(0)
		f.close()
	
	def __readCOCA(self):
		f = open(DictStemmer.__COCAFile, "r")
		for line in f:
			matchObj = re.match(DictStemmer.CocaLineR, line)
			if (matchObj):
				curWord = matchObj.group(2)
				freq = matchObj.group(1)
				pos = matchObj.group(3)
				#self.wordsInfo[curWord] = self.wordsInfo.get(curWord,"") + "C"
				self.wordsInfo[curWord + "$" + pos] = self.wordsInfo.get(curWord + "$" + pos,"") + "C"
				self.cocaWordsInfo[curWord] = self.cocaWordsInfo.get(curWord,"") + pos
				self.cocaWordsFreq[curWord + "$" + pos] = freq
			else:
				logging.warning("COCA line is not recognizable: %s" % line)
				assert(0)
		f.close()
				
	def __doMap(self, pos, chinese, curWord, comment):
		posRe = r"([a-zA-Z]+)"
		posList = re.findall(posRe, pos)
		for p in posList:
			try:
				p = self.LongPos2CocaPos[p]
			except KeyError:
				logging.warning("Can't map %s to (%s, %s)" % (chinese, curWord, pos))
				continue
			assert(len(p) == 1)
			self.WordsMeaning[curWord + "$" + p] = self.WordsMeaning.get(curWord + "$" + p, "") + chinese
			self.wordsInfo[curWord + "$" + p] = self.wordsInfo.get(curWord + "$" + p,"") + comment
		
	
	def __analyzeMeaning(self, line, curWord, comment):
		posRe = r"[a-zA-Z\./]+"
		chineseRe = r"(?:[^a-zA-Z\.]+)"
		itemsR = Template(r'''($posRe)($chineseRe)''').substitute(locals())
		
		line = line.strip()
		lineItems = re.findall(itemsR, line)
		for item in lineItems:
			pos = item[0]
			chinese = item[1]
			self.__doMap(pos, chinese, curWord, comment)

	
	def __readGre(self):
		f = open(DictStemmer.__GRE, "r",encoding="utf_8")
		for line in f:
			match1stLine = re.match(DictStemmer.Gre1stLineR, line)
			match2ndLine = re.match(DictStemmer.Gre2ndLineR, line)
			if (match1stLine):
				curWord = match1stLine.group(0)
				#self.wordsInfo[curWord] = self.wordsInfo.get(curWord,"") + "G"
			elif (match2ndLine):
				self.__analyzeMeaning(line, curWord, "G")
			else:
				logging.warning("GRE line is not recognizable: %s" % line)
		f.close()


	def __readTofel(self):
		f = open(DictStemmer.__Tofel, "r")
		for line in f:
			match1st = re.match(DictStemmer.Tofel1stLineR, line)
			match2nd = re.match(DictStemmer.Tofel2ndLineR, line)
			if (match1st):
				curWord = match1st.group(2)
				curLineNum = match1st.group(1)
				posDesc = match1st.group(3)
				chinese = match1st.group(4)
				#self.wordsInfo[curWord] = self.wordsInfo.get(curWord,"") + "T"
				self.__analyzeMeaning(posDesc + chinese, curWord,  "T")
			elif (match2nd):
				#if (curLineNum != match2nd.group(1)):
				#	print(line + "------")
				assert(curLineNum == match2nd.group(1))
				posDesc = match2nd.group(2)
				chinese = match2nd.group(3)
				#self.__analyzeMeaning(posDesc + chinese, curWord)
				self.__analyzeMeaning(posDesc + chinese, curWord, "T")
			else:
				logging.warning("TOFEL line is not recognizable: %s" % line)
				continue
				#assert(0)

	def doStemming(self, wordAndPos):
		'''
>>> import nltk
>>> nltk.help.upenn_tagset()
$: dollar
    $ -$ --$ A$ C$ HK$ M$ NZ$ S$ U.S.$ US$
'': closing quotation mark
    ' ''
(: opening parenthesis
    ( [ {
): closing parenthesis
    ) ] }
,: comma
    ,
--: dash
    --
.: sentence terminator
    . ! ?
:: colon or ellipsis
    : ; ...
CC: conjunction, coordinating
    & 'n and both but either et for less minus neither nor or plus so
    therefore times v. versus vs. whether yet
CD: numeral, cardinal
    mid-1890 nine-thirty forty-two one-tenth ten million 0.5 one forty-
    seven 1987 twenty '79 zero two 78-degrees eighty-four IX '60s .025
    fifteen 271,124 dozen quintillion DM2,000 ...
DT: determiner
    all an another any both del each either every half la many much nary
    neither no some such that the them these this those
EX: existential there
    there
FW: foreign word
    gemeinschaft hund ich jeux habeas Haementeria Herr K'ang-si vous
    lutihaw alai je jour objets salutaris fille quibusdam pas trop Monte
    terram fiche oui corporis ...
IN: preposition or conjunction, subordinating
    astride among uppon whether out inside pro despite on by throughout
    below within for towards near behind atop around if like until below
    next into if beside ...
JJ: adjective or numeral, ordinal
    third ill-mannered pre-war regrettable oiled calamitous first separable
    ectoplasmic battery-powered participatory fourth still-to-be-named
    multilingual multi-disciplinary ...
JJR: adjective, comparative
    bleaker braver breezier briefer brighter brisker broader bumper busier
    calmer cheaper choosier cleaner clearer closer colder commoner costlier
    cozier creamier crunchier cuter ...
JJS: adjective, superlative
    calmest cheapest choicest classiest cleanest clearest closest commonest
    corniest costliest crassest creepiest crudest cutest darkest deadliest
    dearest deepest densest dinkiest ...
LS: list item marker
    A A. B B. C C. D E F First G H I J K One SP-44001 SP-44002 SP-44005
    SP-44007 Second Third Three Two * a b c d first five four one six three
    two
MD: modal auxiliary
    can cannot could couldn't dare may might must need ought shall should
    shouldn't will would
NN: noun, common, singular or mass
    common-carrier cabbage knuckle-duster Casino afghan shed thermostat
    investment slide humour falloff slick wind hyena override subhumanity
    machinist ...
NNP: noun, proper, singular
    Motown Venneboerger Czestochwa Ranzer Conchita Trumplane Christos
    Oceanside Escobar Kreisler Sawyer Cougar Yvette Ervin ODI Darryl CTCA
    Shannon A.K.C. Meltex Liverpool ...
NNPS: noun, proper, plural
    Americans Americas Amharas Amityvilles Amusements Anarcho-Syndicalists
    Andalusians Andes Andruses Angels Animals Anthony Antilles Antiques
    Apache Apaches Apocrypha ...
NNS: noun, common, plural
    undergraduates scotches bric-a-brac products bodyguards facets coasts
    divestitures storehouses designs clubs fragrances averages
    subjectivists apprehensions muses factory-jobs ...
PDT: pre-determiner
    all both half many quite such sure this
POS: genitive marker
    ' 's
PRP: pronoun, personal
    hers herself him himself hisself it itself me myself one oneself ours
    ourselves ownself self she thee theirs them themselves they thou thy us
PRP$: pronoun, possessive
    her his mine my our ours their thy your
RB: adverb
    occasionally unabatingly maddeningly adventurously professedly
    stirringly prominently technologically magisterially predominately
    swiftly fiscally pitilessly ...
RBR: adverb, comparative
    further gloomier grander graver greater grimmer harder harsher
    healthier heavier higher however larger later leaner lengthier less-
    perfectly lesser lonelier longer louder lower more ...
RBS: adverb, superlative
    best biggest bluntest earliest farthest first furthest hardest
    heartiest highest largest least less most nearest second tightest worst
RP: particle
    aboard about across along apart around aside at away back before behind
    by crop down ever fast for forth from go high i.e. in into just later
    low more off on open out over per pie raising start teeth that through
    under unto up up-pp upon whole with you
SYM: symbol
    % & ' '' ''. ) ). * + ,. < = > @ A[fj] U.S U.S.S.R * ** ***
TO: "to" as preposition or infinitive marker
    to
UH: interjection
    Goodbye Goody Gosh Wow Jeepers Jee-sus Hubba Hey Kee-reist Oops amen
    huh howdy uh dammit whammo shucks heck anyways whodunnit honey golly
    man baby diddle hush sonuvabitch ...
VB: verb, base form
    ask assemble assess assign assume atone attention avoid bake balkanize
    bank begin behold believe bend benefit bevel beware bless boil bomb
    boost brace break bring broil brush build ...
VBD: verb, past tense
    dipped pleaded swiped regummed soaked tidied convened halted registered
    cushioned exacted snubbed strode aimed adopted belied figgered
    speculated wore appreciated contemplated ...
VBG: verb, present participle or gerund
    telegraphing stirring focusing angering judging stalling lactating
    hankerin' alleging veering capping approaching traveling besieging
    encrypting interrupting erasing wincing ...
VBN: verb, past participle
    multihulled dilapidated aerosolized chaired languished panelized used
    experimented flourished imitated reunifed factored condensed sheared
    unsettled primed dubbed desired ...
VBP: verb, present tense, not 3rd person singular
    predominate wrap resort sue twist spill cure lengthen brush terminate
    appear tend stray glisten obtain comprise detest tease attract
    emphasize mold postpone sever return wag ...
VBZ: verb, present tense, 3rd person singular
    bases reconstructs marks mixes displeases seals carps weaves snatches
    slumps stretches authorizes smolders pictures emerges stockpiles
    seduces fizzes uses bolsters slaps speaks pleads ...
WDT: WH-determiner
    that what whatever which whichever
WP: WH-pronoun
    that what whatever whatsoever which who whom whosoever
WP$: WH-pronoun, possessive
    whose
WRB: Wh-adverb
    how however whence whenever where whereby whereever wherein whereof why
``: opening quotation mark
    ` ``
		'''
		longPos2ShortPos = {
			 'CC':'c', 
			 #'CD'
			 'DT':'d',
			 'EX':'r',
			 #'FW':	 #需要特别处理
			 'IN':'i',
			 'JJ':'j',
			 'JJR':'j',
			 'JJS':'j',
			 'LS':'j',
			 'MD':'v',
			 'NN':'n',
			 #'NNP'
			 #'NNPS'
			 'NNS':'n', #名词复数，需要stem一次
			 'PDT':'d',
			 #POS
			 'PRP':'p',
			 'PRP$':'p',
			 'RB':'r',
			 'RBR':'r', # 可按照jjr来处理
			 'RBS':'r', # 可按照jjs来处理
			 'RP':'i',
			 #'SYM'
			 #'TO'
			 #'UH'
			 'VB':'v',
			 'VBD':'v', # 需要stem一次
			 'VBG':'v', # 需要stem一次
			 'VBN':'v', # 需要stem一次
			 'VBP':'v',
			 'VBZ':'v', # 需要stem一次
			 'WDT':'d',
			 'WP':'p',
			 'WP$':'d',
			 'WRB':'r',
			 #'\'\'':
		}
	
		simpleStem = {
		#做简单的变换，比如 名词复数变单数，形容词比较级最高级变原型，动词时态变动词标准型
			 'CC':0,
			 #'CD'
			 'DT':0,
			 'EX':0,
			 #'FW':	 需要特别处理
			 'IN':0,
			 'JJ':0,
			 'JJR':1,
			 'JJS':1,
			 'LS':0,
			 'MD':0,
			 'NN':0,
			 #'NNP'
			 #'NNPS'
			 'NNS':1, #名词复数，需要stem一次
			 'PDT':0,
			 #POS
			 'PRP':0,
			 'PRP$':0,
			 'RB':0,
			 'RBR':1, # 可按照jjr来处理
			 'RBS':1, # 可按照jjs来处理
			 'RP':0,
			 #'SYM'
			 #'TO'
			 #'UH'
			 'VB':0,
			 'VBD':1, # 需要stem一次
			 'VBG':1, # 需要stem一次
			 'VBN':1, # 需要stem一次
			 'VBP':0,
			 'VBZ':1, # 需要stem一次
			 'WDT':0,
			 'WP':0,
			 'WP$':0,
			 'WRB':0,
			 #'\'\'':
		}
		
		complexStem = [
			['r', r'.+ly\b', r'j', r'ly\b'],
			['j', r'.+ful\b', r'n', r'ful\b'],
			['n', r'.+fulness\b', r'n|v|j', r'fulness\b'],
			['n', r'.+ness\b', r'j', r'ness\b'],
		]
		
		(word, Pos) = wordAndPos
		word = word.lower()
		if (Pos in longPos2ShortPos):
			if (Pos in simpleStem and simpleStem[Pos] > 0):
				if (word in self.cocaDict):
					(oldword, word) = (word, self.cocaDict[word])
					Pos = longPos2ShortPos[Pos]
					logging.debug("(%s, %s) -> %s" % (oldword, Pos, word))
				else:
					raise NoWordInDict # "No Word avaiilable"
			else:
				Pos = longPos2ShortPos[Pos]
				
			for trans in complexStem:
				if (Pos == trans[0]  and  # 词性
					 re.match(trans[1], word) and  # 匹配正则表达式
					 re.sub(trans[3], "", word) in self.cocaDict and  # 将词缀抹去，该词在字典中
					 re.match(trans[2], self.cocaWordsInfo.get(re.sub(trans[3], "", word), ""))
					 ):
					 	(oldword, word) = (word, re.sub(trans[3], "", word))
					 	(oldPos, Pos) = (Pos, self.cocaWordsInfo.get(word, "")[0])
					 	logging.debug("(%s, %s) -> (%s, %s)" % (oldword, oldPos, word, Pos))
				elif (Pos == trans[0]  and  # 词性
				   re.match(trans[1], word) and  # 匹配正则表达式
				   word in self.cocaDict and  # 存在词转换映射
				   re.match(trans[2], self.cocaWordsInfo.get(self.cocaDict[word], "")) and # 转换词满足词性
				   not re.match(trans[1], self.cocaDict[word]) # 词缀 在 转换词中已经被去掉了 
				   ):
					(oldword, word) = (word, self.cocaDict[word])
					(oldPos, Pos) = (Pos, self.cocaWordsInfo.get(word, "")[0])
					logging.debug("(%s, %s) -> (%s, %s)" % (oldword, oldPos, word, Pos))
				else:
					continue
			return (word, Pos)
		elif (Pos == 'FW'):
			if (word in self.cocaDict or word in self.cocaMainWord):
				Pos = self.cocaWordsInfo.get(word, "")
				if (len(Pos) == 0):
					raise COCAPosInfoNotExist #"No Pos available" 
				else:
					Pos = Pos[0]
				return (word, Pos)
			else:
				raise NoWordInDict # "No Word avaiilable"
		else:
			raise SkipThisWord # "We don't handle the POS, skip this word"
		

			
	