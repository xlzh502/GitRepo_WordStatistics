# coding=gbk

import logging, logging.config
import re
import nltk
from string import Template
import pdb
from DictStemmer import DictStemmer, NoWordInDict, COCAPosInfoNotExist, SkipThisWord
#import dpath.util
from datetime import datetime
import itertools
from functools import cmp_to_key
from SynonymAnalyze import SynonyAnalyzer
import yaml
import codecs


#logging.basicConfig(format='%(levelname)s:%(message)s',  filename="c:\\GRE 词频统计\\logging.txt", filemode='w', level=logging.DEBUG)
#logging.basicConfig(format='%(message)s',  filename="c:\\GRE 词频统计\\finalResult.txt", filemode='w', level=logging.CRITICAL)
with codecs.open("./ConfigureLogger.yml", 'r', 'utf-8') as f:
	D=yaml.load(f)
	logging.config.dictConfig(D)



	


def getChapID(strs):
	refer = {"I" : 1, "II" : 2, "III" : 3, "IV" : 4, "V" : 5, "VI" : 6, "VII" : 7, "VIII" : 8, "IX" : 9, "X" : 10, 
         "XI" : 11, "XII" : 12, "XIII" : 13, "XIV" : 14, "XV" : 15, "XVI" : 16, "XVII" : 17, "XVIII" : 18, "XIX" : 19, "XX" : 20, 
         "XXI" : 21, "XXII" : 22, "XXIII" : 23, "XXIV" : 24, "XXV" : 25, "XXVI" : 26, "XXVII" : 27, "XXVIII" : 28, "XXIX" : 29, "XXX" : 30, 
         "XXXI" : 31, "XXXII" : 32, "XXXIII" : 33, "XXXIV" : 34, "XXXV" : 35, "XXXVI" : 36, "XXXVII" : 37, "XXXVIII" : 38, "XXXIX" : 39, "XL" : 40,
         "XLI" : 41, "XLII" : 42, "XLIII" : 43, "XLIV" : 44, "XLV" : 45, "XLVI" : 46, "XLVII" : 47, "XLVIII" : 48, "XLIX" : 49, "L" : 50, 
         "LI" : 51, "LII" : 52, "LIII" : 53, "LIV" : 54, "LV" : 55, "LVI" : 56, "LVII" : 57, "LVIII" : 58, "LIX" : 59, "LX" : 60, 
         "LXI" : 61, "LXII" : 62, "LXIII" : 63, "LXIV" : 64, "LXV" : 65, "LXVI" : 66, "LXVII" : 67, "LXVIII" : 68, "" : None}
	volId, chapId = ("", "")
	
	volumnReXp=r'''\s*
               (?:VOLUMN|VOLUME|VOL\.|BOOK)  # VOLUMN  VOL.
               [ ]               # spaces
               ([IVXL]+)         # VOL. I.
               
               '''


	chapReXp=r'''\s*
             (?:CHAPTER|Chapter)
             [ ]
             ([0-9IVXL]+)
             
          '''

	breakReXp=Template(r'''
     ^(?:$volumnReXp.*?)?
     ^(?:$chapReXp)
     ''').substitute(locals())
	
	
	if re.match(breakReXp, strs, re.M| re.S | re.VERBOSE):
		volId, chapId = re.findall(breakReXp, strs, re.M| re.S | re.VERBOSE)[0]

	if (volId in refer.keys()):
		volId = refer[volId]
	else:
		volId = int(volId)
	
	if (chapId in refer.keys()):
		chapId = refer[chapId]
	else:
		chapId = int(chapId)

	return (volId, chapId)

pdb.set_trace() 


NovelList = [
						['Lord of the flies.txt', 'gbk'],
						["CNN.txt", 'latin_1'],
						['Gone with the wind.txt', 'gbk'], #已经接近读完
						['pride and prejudice.txt', 'gbk'], #有录音
						['david copperfield.txt', 'utf_8_sig'],#有录音
						['Emma.txt', 'gbk'],#有录音
						['hard times.txt', 'utf_8_sig'], #有录音
						['Jane Eyre.txt', 'gbk'], #有录音
						['lord jim.txt', 'utf_8_sig'],#有录音
						['Mansfield Park.txt', 'gbk'],#有录音
						['martin chuzzlewit.txt', 'utf_8_sig'],#有录音
						['Northanger Abbey.txt', 'gbk'],
						['oliver twist.txt', 'gbk'],
						['Persuasion.txt', 'gbk'],
						['sense and sensibility.txt','gbk'],
						['Sister Carrie.txt','gbk'],
						['sons and lovers.txt','gbk'],
						['Tess of the Urbervilles.txt','gbk'],
						['the adventure of tom sawyer.txt','utf_8_sig'],
						['The count of monte Cristo.txt','gbk'],
						#['The genius.txt','gbk'],
						['the mayor of casterbridge.txt','gbk'],
						['the moonstone.txt','gbk'],
						['the return of the native.txt','utf_8_sig'],
						['Treasure Island.txt','gbk'],
						['Wuthering Heights.txt','gbk'],
						['the Adventures of Huckleberry Finn.txt', 'utf_8_sig'],
						['Lost Horizon.txt', 'latin_1'],
						['The sun also rises.txt', 'gbk'],
						['The old man and the sea.txt', 'utf_8_sig'],	
						['The Life of the Bee.txt', 'utf_8_sig'],	
						['A tale of two cities.txt', 'latin_1'],
						['Agnes Grey.txt', 'utf_8_sig'],
						['The call of the wild.txt', 'utf_8_sig'],
						['White fang.txt', 'utf_8_sig'],
						['The sea wolf.txt', 'utf_8_sig'],
						['An inquiry into the nature and causes of the wealth of nations.txt',  'utf_8_sig'],
						["A collection of english language children's literature.txt", 'gbk'],
						['My Life by Bill Clinton.txt', 'utf_8_sig'], # 先排除这个长篇
						['The client.txt','utf_8_sig'],
						['The Lincoln Lawyer.txt','utf_8_sig'],
						['A complete collection of tails by Edgar Allan Poe.txt','gbk'],
						#['East of Eden.txt','latin_1'],
						#['The Art of Fielding.txt','latin_1'],
						["Sophie's World.txt",'utf_8_sig'],
						["The Help.txt",'gbk'],
						["Water for elephants.txt",'gbk'],
						["Atlas Shrugged.txt",'utf_8_sig'],
						["The Fountainhead.txt", 'utf_8_sig'],
						["The Godfather.txt", 'utf_8_sig'],
						["One Hundred Years Of Solitude.txt", 'utf_8_sig'],
						["Under the Dome.txt", 'utf_8_sig'],
						["Kite Runner.txt", 'utf_8_sig'],
						["To Kill A Mockingbird.txt", 'latin_1'],
						["The Storied Life of A. J. Fikry.txt", 'utf_8_sig'],
						['selected short stories of O Henry.txt', 'utf_8_sig'],
						['Gennie Gerhardt.txt', 'utf_8_sig'],
						['Ulysses.txt', 'utf_8_sig'],
						['Vanity Fair.txt', 'utf_8_sig'],
            ]



def printHelp():
	for novel in NovelList:
		print("[%d] %s" % (NovelList.index(novel), novel[0]))


def chapVolId(chapId, volId = None, encoding = 0):
	if (encoding != 0):
		if (volId != None):
			return volId * 1000000000 + chapId
		else:
			return chapId
	else:
		volId = chapId // 1000000000
		chapId = chapId % 1000000000
		if (volId == 0):
			return str(chapId)
		else:
			return str(volId) + "." + str(chapId)

def getChapMaps(bookName, enc):
	chapContents = {}
	lastChapId = None
	lastVolId = None
	
	volumnReXp=r'''\s*
               (?:VOLUME|VOL\.|BOOK)  # VOLUMN  VOL.
               [ ]               # spaces
               (?:[IVXL]+)         # VOL. I.
               (?=[^IVXL])       # end of VOLUMN
               '''
	chapReXp=r'''\s*
	             (?:CHAPTER|Chapter)
	             [ ]
	             (?:[0-9IVXL]+)
	             (?=[^0-9IVXL])
	          '''
	breakReXp=Template(r'''(
	                  ^(?:$volumnReXp.*?)?
										^(?:$chapReXp)
										)''').substitute(locals())
	try:
		txtFile = open(str('./YuLiaoKu/') + bookName, mode = 'rt', encoding = enc)
	except ValueError:
		print("Open <%s> error." % bookName)
	raw=txtFile.read()
	breakRe=re.compile(breakReXp, re.M | re.S | re.VERBOSE)
	chapList=re.split(breakRe, raw)
	
	for chap in chapList:
		volId, chapId = getChapID(chap)
		if (chapId != None):
			lastChapId = chapId
			if (volId != None):
				lastVolId = volId
		elif (lastChapId != None):
			# handle chapter contents
			if (lastVolId != None):
				# if we have book II  chap 10, then we need 2.10, but in float format, 2.10 == 2.1, which will introduce confusion
				# so save (volId, chapId) in format like:  volId * 1000 + chapId
				chapContents[chapVolId(lastChapId, lastVolId, encoding = 1)] = chap
			else:
				chapContents[chapVolId(lastChapId, encoding = 1)] = chap
		else:
			continue
	return chapContents
	
	
def enumerateDic(dic):
	unpack = [i for i in dic.values()]
	while (1):
		iterator = iter(unpack)
		try:
			curItem = next(iterator)
		except StopIteration:
			break
		if (hasattr(curItem, "__iter__")):
			unpack = itertools.chain(curItem.values(), iterator)
		else:
			yield curItem
			unpack = iterator

def updateBookChapWords(bookChapWords, bookName, chapId, word, Pos):
	if (bookName not in bookChapWords):
		bookChapWords[bookName] = {}
	if (chapId not in bookChapWords[bookName]):
		bookChapWords[bookName][chapId] = {}
	if (word+"$"+Pos not in bookChapWords[bookName][chapId]):
		bookChapWords[bookName][chapId][word + "$" + Pos] = 0
		
def updateWordOccurence(wordOccurrence, word, Pos, bookName, chap):
	if (word not in wordOccurrence):
		wordOccurrence[word] = {}
	if (Pos not in wordOccurrence[word]):
		wordOccurrence[word][Pos] = {}
	if (bookName not in wordOccurrence[word][Pos]):
		wordOccurrence[word][Pos][bookName] = {}
	if (chapId not in wordOccurrence[word][Pos][bookName]):
		wordOccurrence[word][Pos][bookName][chapId] = 1
	else:
		wordOccurrence[word][Pos][bookName][chapId] += 1

def getWordMark(wordPos):
	isGre = " "
	isTofel = " "
	if (re.search("G|K", stemmer.wordsInfo[wordPos])):
		isGre = "G"
	if (re.search("T", stemmer.wordsInfo[wordPos])):
		isTofel = "T"
	return "[" + isGre + isTofel + "]"

def sortByFreqAndAlphabet(occurCounts):
	def Impl(wordPos1, wordPos2):
		'''先按照词性归类， 对于相同词性的单词，按照 词频排序， 在词频相同的情形下，按照字典顺序排序'''
		# use the expression (a > b) - (a < b) as the equivalent for cmp(a, b)
		a = occurCounts.get(wordPos1, 0)
		b = occurCounts.get(wordPos2, 0)
		freqOrder = (a > b) - (a < b)
		alphaOrder = (wordPos1 > wordPos2) - (wordPos1 < wordPos2)
		pos1 = re.split(r"[$]", wordPos1)[1]
		pos2 = re.split(r"[$]", wordPos2)[1]
		posOrder = (pos1 > pos2) - (pos1 < pos2)
		if (posOrder):
			return posOrder
		elif (freqOrder):
			return freqOrder
		else:
			return alphaOrder
	return Impl
		
def genCompactChaps(chapVolIds):
	'''给定一个章节的列表， 返回压缩后的章节列表，譬如:
	 3,5,6,8,9,10,11,13
	 返回:
	 3,5,6,8-11,13
	'''
	result = []
	if (len(chapVolIds) == 1):
		return [chapVolId(chapVolIds[0])]
	# 计算各个章与前一章的 差值
	deltaList = [ chapVolIds[i] - chapVolIds[i-1] for i in range(1, len(chapVolIds)) ]
	deltaList.insert(0,0)
	i = 0
	while (i < len(deltaList)):
		while (i < len(deltaList)-1 and deltaList[i+1] != 1):
			result.append(chapVolId(chapVolIds[i]))
			i+=1
		if (i == len(deltaList) - 1):
			result.append(chapVolId(chapVolIds[i]))
			break
		else:
			j = i + 1
		while (j < len(deltaList)-1 and deltaList[j+1] == 1):
			j+=1
		if (j - i > 1):
			result.append("%s-%s" % (chapVolId(chapVolIds[i]), chapVolId(chapVolIds[j])))
		else:
			result.append(chapVolId(chapVolIds[i]))
			result.append(chapVolId(chapVolIds[j]))
		i=j+1
	return result

def genCompressWord(word):
	'''It is sometimes noted that English text is highly redundant, and it is still easy to read when word-internal vowels are left out. 
	For example, declaration becomes dclrtn, and inalienable becomes inlnble, retaining any initial or final vowel sequences. 
	The regular expression in our next example matches initial vowel sequences, final vowel sequences, and all consonants; everything else is ignored. 
	This three-way disjunction is processed left-to-right, if one of the three parts matches the word, any later parts of the regular expression are ignored.'''
	regexp = r'^[AEIOUaeiou]+|[AEIOUaeiou]+$|[^AEIOUaeiou]'
	pieces = re.findall(regexp, word)
	return ''.join(pieces)

def cmprssBookName(bookName):
	return  "".join(genCompressWord(word).capitalize() for word in re.split(" ", bookName))

def getSynonyms(wordPos, symSet1, symSet2, wordPosInterested, sortFunc):
	word, pos = re.split(r"[$]", wordPos)
	result = ''
	if word in symSet1:
		if pos in symSet1[word]:
			cnt = 1
			for idx in symSet1[word][pos]:
				wordPosSet = set([w + '$' + pos for w in symSet1[word][pos][idx]])
				wordPosFirst = wordPosSet & wordPosInterested
				wordPosSecond = wordPosSet - wordPosFirst
				sortSet1 = [re.split(r"[$]", m)[0] for m in sorted(wordPosFirst, key = cmp_to_key(sortFunc))]
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
				sortSet1 = [re.split(r"[$]", m)[0] for m in sorted(wordPosFirst, key = cmp_to_key(sortFunc))]
				sortSet2 = [re.split(r"[$]", m)[0] for m in sorted(wordPosSecond)]
				result += 'SymSet_2 %d[%s]\n' % (cnt, ", ".join(sortSet1) + ' ●' + ", ".join(sortSet2))
				cnt += 1
	return result
		
				

starttime = datetime.now()
stemmer = DictStemmer()
synonymSet1 = SynonyAnalyzer("./DUMP Oxford Synonyms.txt").startParse()
synonymSet2 = SynonyAnalyzer("./DUMP Soule's Dictionary of English Synonyms.txt").startParse()
endtime = datetime.now()
logging.info("Stemmer initialized: %d s" % (endtime - starttime).seconds)

if (0):
	#先统计一边，G和K的差集
	print("先统计红皮书 与 绿皮书 之间的差集")
	wordInNEWGRE = set(re.split(r"[$]", wordPos)[0] for wordPos in stemmer.wordsInfo if re.search("K", stemmer.wordsInfo[wordPos]))
	wordInOLDGRE = set(re.split(r"[$]", wordPos)[0]  for wordPos in stemmer.wordsInfo if re.search("G", stemmer.wordsInfo[wordPos]))
	wordsOnlyInNew = wordInNEWGRE - wordInOLDGRE
	wordsBoth = wordInNEWGRE & wordInOLDGRE
	wordsOnlyInOld = wordInOLDGRE - wordInNEWGRE
	logging.critical("---------------words of NEW GRE %d, words of Old GRE %d, N && O %d, N - O %d, O - N %d -------------" 
	                % (len(wordInNEWGRE), len(wordInOLDGRE), len(wordsBoth), len(wordsOnlyInNew), len(wordsOnlyInOld)))
	maxWordLen = max(len(word) for word  in wordsOnlyInNew)
	logging.critical("--------------- Words occured ONLY in NEW GRE --------")
	for word in sorted(wordsOnlyInNew):
		for wordPos in [ wordPos for wordPos in stemmer.WordsMeaning if wordPos.startswith(word+"$") ]:
			Pos = re.split(r"[$]", wordPos)[1]
			logging.critical("%-" + str(maxWordLen+1) + "s%2s %s", word, Pos, re.sub(r'（.+?）', "", stemmer.WordsMeaning[wordPos]))
	maxWordLen = max(len(word) for word  in wordsOnlyInOld)
	logging.critical("--------------- Words occured ONLY in OLD GRE --------")
	for word in sorted(wordsOnlyInOld):
		for wordPos in [ wordPos for wordPos in stemmer.WordsMeaning if wordPos.startswith(word+"$") ]:
			Pos = re.split(r"[$]", wordPos)[1]
			logging.critical("%-" + str(maxWordLen+1) + "s%2s %s", word, Pos, stemmer.WordsMeaning[wordPos])
	#logging.critical("--------------- Words Both occured in OLD and NEW GRE --------")
	#maxWordLen = max(len(word) for word  in wordsBoth)
	#for word in sorted(wordsBoth):
	#	for wordPos in [ wordPos for wordPos in stemmer.WordsMeaning if wordPos.startswith(word+"$") ]:
	#		Pos = re.split(r"[$]", wordPos)[1]
	#		logging.critical("%-" + str(maxWordLen+1) + "s%2s %s", word, Pos,  re.sub(r'（.+?）', "", stemmer.WordsMeaning[wordPos]))


wordPosInterested = set(wordPos for wordPos in stemmer.wordsInfo if re.search("G|T|K", stemmer.wordsInfo[wordPos]))
wordsInterested = set(re.split(r"[$]", wordPos)[0] for wordPos in wordPosInterested)

#logging.critical("-------- 打印 一个 数组 ---------")
#for word in sorted(wordsInterested):
#	logging.critical("\"%s\"," % word)
#logging.critical("-------- end ---------")


#本来，我是打算使用dpath.util.search的，但是发现，执行起来非常慢。所以，只能用wordOccurrence、chapContains来统计信息了。
wordOccurrence = {}  # 统计各个词 在每本书的每一章 出现的次数
bookChapWords = {}  # 统计每本书的每一章， 出现了哪些单词
for novelInfo in NovelList:
	starttime = datetime.now()
	chapContents = getChapMaps(novelInfo[0], novelInfo[1])
	bookName = re.sub(r"\.txt", "", novelInfo[0])
	logging.getLogger('DictStemmer').info("handling %s, %d of %d" % (bookName, NovelList.index(novelInfo) + 1, len(NovelList)))
	logging.info("handling %s, %d of %d" % (bookName, NovelList.index(novelInfo) + 1, len(NovelList)))
	for chapId in sorted(chapContents.keys()):
		chap = chapContents[chapId]
		sents = nltk.sent_tokenize(chap)
		for sent in sents:
			tokens = nltk.word_tokenize(sent)
			tokenPOS = nltk.pos_tag(tokens)
			logging.getLogger('DictStemmer').info(re.sub(r'\n+', ' ', sent))
			logging.getLogger('DictStemmer').info(tokenPOS)
			for wordAndPos in tokenPOS:
				try:
					(word, Pos) = stemmer.doStemming(wordAndPos)
					if (word+'$'+Pos in wordPosInterested):
						logging.getLogger('DictStemmer').info("(%s, %s)"%(word, Pos))
						updateWordOccurence(wordOccurrence, word, Pos, bookName, chapId)
						updateBookChapWords(bookChapWords, bookName, chapId, word, Pos)
				except NoWordInDict:
					logging.getLogger('DictStemmer').error("(%s, %s) not in DICT"%(wordAndPos[0], wordAndPos[1]))
					continue
				except COCAPosInfoNotExist:
					logging.getLogger('DictStemmer').error("(%s, %s) not have POS"%(wordAndPos[0], wordAndPos[1]))
					continue
				except SkipThisWord:
					logging.getLogger('DictStemmer').info("(%s, ---)" % wordAndPos[0])
					continue
	endtime = datetime.now()
	logging.info("Handing novel <%s>: %d s" % (bookName, (endtime - starttime).seconds))

occurCounts = {}
for word in wordOccurrence:
	for Pos in wordOccurrence[word]:
		occurCounts[word+"$"+Pos] = sum(enumerateDic(wordOccurrence[word][Pos]))





print("------------- Print All GRA|Toefl words: 用来使用aboboo软件，听发音 ------------")
logging.getLogger('Voc').critical("------------- Print All GRA|Toefl words: 用来使用aboboo软件，听发音 ------------")
for word in sorted(wordsInterested):
	logging.getLogger('Voc').critical("%s", word)
	

#打印各个书的章节中的词（按照字母顺序）
starttime = datetime.now()
for bookName in bookChapWords:
	logging.getLogger(bookName).critical("-------------- Print words according to alphabet order ------------------------")
	for chap in sorted(bookChapWords[bookName]):
		logging.getLogger(bookName).critical("--------------------------------------\n  %s,  Chapter %s \n--------------------------------------" % (bookName, chapVolId(chap)))
		wordsToPrint =  set(wordPos for wordPos in bookChapWords[bookName][chap])  & wordPosInterested
		if (len(wordsToPrint) == 0):
			continue
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
		for wordPos in sorted(wordsToPrint):
			word, Pos = re.split(r"[$]", wordPos)
			logging.getLogger(bookName).critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的章节中的词（按照词频顺序，最少出现词最先打印）
starttime = datetime.now()
for bookName in bookChapWords:
	logging.getLogger(bookName).critical("-------------- Print words according to word frequency order ------------------------")
	for chap in sorted(bookChapWords[bookName]):
		logging.getLogger(bookName).critical("--------------------------------------\n  %s,  Chapter %s \n--------------------------------------" % (bookName, chapVolId(chap)))
		wordsToPrint =  set(wordPos for wordPos in bookChapWords[bookName][chap])  & wordPosInterested
		if (len(wordsToPrint) == 0):
			continue
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
		for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet(occurCounts))):
			word, Pos = re.split(r"[$]", wordPos)
			logging.getLogger(bookName).critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()


#打印各个书的单词（按照字母顺序）
starttime = datetime.now()
for bookName in bookChapWords:
	logging.getLogger(bookName).critical("-------------- Book word summary, print words according to alphabet order ------------------------")
	logging.getLogger(bookName).critical("--------------------------------------\n  <%s> word summary (alphabet order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	if (len(wordsToPrint) == 0):
		continue
	maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
	for wordPos in sorted(wordsToPrint):
		word, Pos = re.split(r"[$]", wordPos)
		#occurChaps = list(chapVolId(chapVol) for chapVol in sorted(wordOccurrence[word][Pos][bookName]))
		occurChaps = genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))
		logging.getLogger(bookName).critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d,%-2d] %s [%s]", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], ','.join(occurChaps))
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的单词（按照词频顺序，最少出现词最先打印）
starttime = datetime.now()
for bookName in bookChapWords:
	logging.getLogger(bookName).critical("-------------- Book word summary, print words according to word frequency order ------------------------")
	logging.getLogger(bookName).critical("--------------------------------------\n  <%s> word summary (word frequency order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	if (len(wordsToPrint) == 0):
		continue
	maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
	for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet(occurCounts))):
		word, Pos = re.split(r"[$]", wordPos)
		occurChaps = genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))
		logging.getLogger(bookName).critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d,%-2d]  %s [%s]", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], ','.join(occurChaps))
endtime = datetime.now()


#按照单词，打印各个单词出现在各本书的名称
logging.getLogger('Voc').critical("-------------- Word Summary, print words according to alphabet order ------------------------")
starttime = datetime.now()
wordsToPrint = set(word+"$"+Pos for word in wordOccurrence for Pos in wordOccurrence[word]) & wordPosInterested
maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
for wordPos in sorted(wordsToPrint):
	word, Pos = re.split(r"[$]", wordPos)
	bookOccurInfo = ""
	for bookName in wordOccurrence[word][Pos]:
		bookOccurInfo += "%s(%d)[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])), ','.join(genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))))
		#bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])))
	logging.getLogger('Voc').critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d] %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], stemmer.WordsMeaning[wordPos], bookOccurInfo)
endtime = datetime.now()
logging.getLogger('Voc').info("Printing word result: %d s" % (endtime - starttime).seconds)

logging.getLogger('Voc').critical("-------------- Word Summary, print words according to frequency order ------------------------")
starttime = datetime.now()
for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet(occurCounts))):
	word, Pos = re.split(r"[$]", wordPos)
	bookOccurInfo = ""
	for bookName in wordOccurrence[word][Pos]:
		bookOccurInfo += "%s(%d)[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])), ','.join(genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))))
		#bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])))
	logging.getLogger('Voc').critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d] %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], stemmer.WordsMeaning[wordPos], bookOccurInfo)
endtime = datetime.now()
logging.getLogger('Voc').info("Printing word result: %d s" % (endtime - starttime).seconds)

# 计算各书出现的GRE词汇的覆盖率
#   先计算 各个书中 出现的 wordPos
logging.getLogger('Coverage').critical("-------------- Word Coverage Rate ------------------------")
wordPosInNovel = {}
wordPosInNovels = set()
for bookName in bookChapWords:
	wordPosInNovel[bookName] = set()
	for chap in sorted(bookChapWords[bookName]):
		for wordPos in bookChapWords[bookName][chap]:
			if (wordPos not in wordPosInterested):
				continue
			wordPosInNovel[bookName].add(wordPos)
			wordPosInNovels.add(wordPos)		
		logging.getLogger('Coverage').info("(%s, %s)  %.2f%%" % (bookName, chapVolId(chap), len(wordPosInNovel[bookName])/len(wordPosInterested)*100))
	logging.getLogger('Coverage').critical("wordPos %s %.2f%%, accumulate %.2f%%" % (bookName, len(wordPosInNovel[bookName]) / len(wordPosInterested)*100, len(wordPosInNovels) / len(wordPosInterested)*100))
	wordsInNovels = set(re.split(r"[$]", wordPos)[0] for wordPos in wordPosInNovels)

# 哪些词在所有小说中，都没有出现过
wordsNotOccur = wordPosInterested - wordPosInNovels
logging.getLogger('Voc').critical("-------------words that don't show in any novels------------")
for wordPos in sorted(wordsNotOccur):
	word, Pos = re.split(r"[$]", wordPos)
	logging.getLogger('Voc').critical("%-17s%2s%5s %s", word, Pos, getWordMark(wordPos), stemmer.WordsMeaning[wordPos])



while (1):	
	printHelp()
	while (1):
		try:
			sumWordPosSet = set()	
			s = input("please input a list of novels for Word Coverage Rate (or help):")
			if (s == 'help' or s == 'h' or s == ''):
				printHelp()
				continue
			seqList = [ int(x) for x in s.split(",") ]
			novels = [ re.sub(r"\.txt", "", x[0]) for x in NovelList ] 
			logging.getLogger('Coverage').info("-------------- Novel Word Coverage Calculation based on: %s -------" % "★".join([novels[i] for i in seqList]))
			for seqId in seqList:
				novelName = novels[seqId]
				novelWordPosSet = wordPosInNovel[novelName]
				sumWordPosSet = sumWordPosSet | novelWordPosSet
				logging.getLogger('Coverage').info("%s = %.2f%%" % (novelName, len(novelWordPosSet)/len(wordPosInterested)*100))
			logging.getLogger('Coverage').info("Sum coverage: %.2f%%" % (len(sumWordPosSet)/len(wordPosInterested)*100))
			for seqId in range(len(novels)):
				if seqId in seqList:
					continue
				novelName = novels[seqId]
				logging.getLogger('Coverage').info("[%d]%s=%.2f%%,  sum %.2f%%" % (seqId, novelName, len(wordPosInNovel[novelName])/len(wordPosInterested)*100, 
																				len(sumWordPosSet | wordPosInNovel[novelName]) / len(wordPosInterested)*100))
		except ValueError:
			print("converting to ints: %s" % s) 
			break
		except IndexError:
			print("index overflow: %s" % s)
			break
	
	
	logging.info("------------- 打印一组 GRE 词汇的测试 ------------")
	printHelp()
	GreRedBookAlphabetOrder=[   ''      , 'affordable', 'aorta'      ,   'attenuate', 'bewilder', 'cabal', 
	                'chaste'  , 'commodious', 'construe'   , 'cumbersome' , 'dent'    , 'discretion',
	                'droplet' , 'enmity'    , 'exhilarate' , 'figment'    , 'frustrate', 'grain',
	                'hemostat', 'impalpable', 'ineluctable', 'interplay'  , 'lampoon'  , 'macabre',
	            'metropolitan', 'nadir'     , 'ogle'       , 'paramount'  , 'phenomena', 'precocious',
	            'provocation' , 'recall'    , 'resigned'   , 'sapphire'   , 'shrewd'   , 'sparse'    ,
	            'stroke'      , 'tamp'      , 'transcend'  , 'unrepentant', 'vindicate', 'zzzzzzzzzzz'   ]
	testRex= {'Simple':r'(?!^)[AEIOUaeiou]+?(?!$)', 'Difficult':r'(?!^)[^AEIOUaeiou]+?(?!$)'}
	while (1):
		s = input("please input a list of novels for Vocabulary Testing (or help):")
		if (s == 'help' or s == 'h' or s == ''):
			printHelp()
			continue
		try:
			seqList = [ int(x) for x in s.split(",") ]
			FinishedBook = [ re.sub(r"\.txt", "", NovelList[i][0]) for i in seqList]
			logging.getLogger('VocTest').critical("------------- 打印一组 GRE 词汇的测试, 基于: %s ------------", "★".join(FinishedBook))
			wordOccurrenceOfStudyedBook = {}
			occurFinishedBookCnts = {}
			for word in wordOccurrence:
				for Pos in wordOccurrence[word]:
					for book in wordOccurrence[word][Pos]:
						if book in FinishedBook:
							if (word not in wordOccurrenceOfStudyedBook):
								wordOccurrenceOfStudyedBook[word] = {}
							if (Pos not in wordOccurrenceOfStudyedBook[word]):
								wordOccurrenceOfStudyedBook[word][Pos] = {}
							wordOccurrenceOfStudyedBook[word][Pos][book] = wordOccurrence[word][Pos][book]
			for word in wordOccurrenceOfStudyedBook:
				for Pos in wordOccurrenceOfStudyedBook[word]:
					occurFinishedBookCnts[word+"$"+Pos] = sum(enumerateDic(wordOccurrenceOfStudyedBook[word][Pos]))
			for degree in ['Simple', 'Difficult']:
				sortWordPosList = sorted([wordPos for wordPos in wordPosInterested if re.search("G", stemmer.wordsInfo[wordPos])])
				for i in range(1,42):
					logging.getLogger('VocTest').critical("-------------" + degree + " Test: GRE RedBook List " + str(i) + " Exercise-----------------")
					chapWordPos = [wp for wp in sortWordPosList if re.split(r"[$]", wp)[0].lower() < GreRedBookAlphabetOrder[i] and re.split(r"[$]", wp)[0] >= GreRedBookAlphabetOrder[i-1]]
					maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in chapWordPos)
					for wordPos in sorted(chapWordPos, key = cmp_to_key(sortByFreqAndAlphabet(occurFinishedBookCnts))):
						word, Pos = re.split(r"[$]", wordPos)
						testWord = re.sub(testRex[degree], "_", word)
						occCount = occurFinishedBookCnts.get(wordPos, 0)
						bookOccurInfo = ""
						if (occCount != 0):
							for bookName in wordOccurrenceOfStudyedBook[word][Pos]:
								occurChaps = genCompactChaps(sorted(wordOccurrenceOfStudyedBook[word][Pos][bookName]))
								bookOccurInfo += "%s(%d)[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrenceOfStudyedBook[word][Pos][bookName])), '.'.join(occurChaps))
						logging.getLogger('VocTest').critical("%-" + str(maxWordLen+3) + "s%2s [%-2d]  %s  %s", testWord, Pos, occCount,  stemmer.WordsMeaning[wordPos], bookOccurInfo)
						logging.getLogger('VocTest').critical("%s" % getSynonyms(wordPos, synonymSet1.synonyms, synonymSet2.synonyms, wordPosInterested, sortByFreqAndAlphabet(occurCounts)))
				
				sortWordPosList = [wordPos for wordPos in wordPosInterested if re.search("K", stemmer.wordsInfo[wordPos])]
				for i in range(1, 44):
					logging.getLogger('VocTest').critical("-------------" + degree + " Test: GRE GreenBook List " + str(i) + " Exercise-----------------")
					chapWordPos = [wordPos for wordPos in sortWordPosList if stemmer.GreenBookWord2ChapId[re.split(r"[$]", wordPos)[0]] == i ]
					maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in chapWordPos)
					for wordPos in sorted(chapWordPos, key = cmp_to_key(sortByFreqAndAlphabet(occurFinishedBookCnts))):
						word, Pos = re.split(r"[$]", wordPos)
						testWord = re.sub(testRex[degree], "_", word)
						occCount = occurFinishedBookCnts.get(wordPos, 0)
						bookOccurInfo = ""
						if (occCount != 0):
							for bookName in wordOccurrenceOfStudyedBook[word][Pos]:
								occurChaps = genCompactChaps(sorted(wordOccurrenceOfStudyedBook[word][Pos][bookName]))
								bookOccurInfo += "%s(%d)[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrenceOfStudyedBook[word][Pos][bookName])), '.'.join(occurChaps))
						logging.getLogger('VocTest').critical("%-" + str(maxWordLen+3) + "s%2s [%-2d]  %s   %s", testWord, Pos, occCount,  stemmer.WordsMeaning[wordPos], bookOccurInfo)
						logging.getLogger('VocTest').critical("%s" % getSynonyms(wordPos, synonymSet1.synonyms, synonymSet2.synonyms, wordPosInterested, sortByFreqAndAlphabet(occurCounts)))
		except ValueError:
			print("converting to ints: %s" % s) 
			break
		except IndexError:
			print("index overflow: %s" % s)
			break
	s = input("Do you want to exit coverage testing and vocbulary testing:")
	if (s == 'y' or s == 'Y'):
		break

books = [book for book in wordPosInNovel.keys()]

logging.getLogger('Coverage').critical("words intersection relationship: (book1, book2) = (wordset1, wordset2, wordset1 & wordset2, wordset1 | wordset2)")
result = []
for (book1, book2) in itertools.combinations(books, 2):
	result.append((book1, book2, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                         len(wordPosInNovel[book2])/len(wordPosInterested)*100, 
	                         len(wordPosInNovel[book1] & wordPosInNovel[book2])/len(wordPosInterested)*100,
	                         len(wordPosInNovel[book1] | wordPosInNovel[book2])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.getLogger('Coverage').critical("(%s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)

result.clear()
logging.getLogger('Coverage').critical("words intersection relationship: (book1, book2, book3) = (wordset1, wordset2, wordset3, wordset1 | wordset2 | wordset3)")
for (book1, book2, book3) in itertools.combinations(books, 3):
	result.append((book1, book2, book3, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                                    len(wordPosInNovel[book2])/len(wordPosInterested)*100,
	                                    len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
	                                    len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.getLogger('Coverage').critical("(%s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)
	                                                       
result.clear()
logging.getLogger('Coverage').critical("words intersection relationship: (book1, book2, book3, book4) = (wordset1, wordset2, wordset3, wordset4, wordset1 | wordset2 | wordset3 | wordset4)")
for (book1, book2, book3, book4) in itertools.combinations(books, 4):
	result.append((book1, book2, book3, book4,
                                    len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
                                    len(wordPosInNovel[book2])/len(wordPosInterested)*100,
                                    len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
                                    len(wordPosInNovel[book4])/len(wordPosInterested)*100, 
	                                  len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3] | wordPosInNovel[book4])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.getLogger('Coverage').critical("(%s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item )
	
	
result.clear()
logging.getLogger('Coverage').critical("words intersection relationship: (book1, book2, book3, book4, book5) = (wordset1, wordset2, wordset3, wordset4, wordset5, wordset1 | wordset2 | wordset3 | wordset4 |wordset5)")
for (book1, book2, book3, book4, book5) in itertools.combinations(books, 5):
	result.append((book1, book2, book3, book4, book5, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book2])/len(wordPosInterested)*100,
	                   len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book4])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book5])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3] | wordPosInNovel[book4] | wordPosInNovel[book5])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.getLogger('Coverage').critical("(%s, %s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)

'''
result.clear()
logging.info("words intersection relationship: (book1, book2, book3, book4, book5, book6) = (wordset1, wordset2, wordset3, wordset4, wordset5, wordset6, wordset1 | wordset2 | wordset3 | wordset4 |wordset5 | wordset6)")
totalCnt = len(list(itertools.combinations(books, 6)))
for n, (book1, book2, book3, book4, book5, book6) in enumerate(itertools.combinations(books, 6)):
	print("handling tuple %d of %d" % (n, totalCnt))
	result.append((book1, book2, book3, book4, book5, book6, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book2])/len(wordPosInterested)*100,
	                   len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book4])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book5])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book6])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3] | wordPosInNovel[book4] | wordPosInNovel[book5] | wordPosInNovel[book6])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.info("(%s, %s, %s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)
'''


