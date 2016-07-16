# coding=gbk

import logging
import re
import nltk
from string import Template
import pdb
from DictStemmer import DictStemmer, NoWordInDict, COCAPosInfoNotExist, SkipThisWord
#import dpath.util
from datetime import datetime
import itertools
from functools import cmp_to_key

#logging.basicConfig(format='%(levelname)s:%(message)s',  filename="c:\\GRE 词频统计\\logging.txt", filemode='w', level=logging.DEBUG)
logging.basicConfig(format='%(message)s',  filename="c:\\GRE 词频统计\\finalResult.txt", filemode='w', level=logging.CRITICAL)

def getChapID(strs):
	refer = {"I" : 1, "II" : 2, "III" : 3, "IV" : 4, "V" : 5, "VI" : 6, "VII" : 7, "VIII" : 8, "IX" : 9, "X" : 10, 
         "XI" : 11, "XII" : 12, "XIII" : 13, "XIV" : 14, "XV" : 15, "XVI" : 16, "XVII" : 17, "XVIII" : 18, "XIX" : 19, "XX" : 20, 
         "XXI" : 21, "XXII" : 22, "XXIII" : 23, "XXIV" : 24, "XXV" : 25, "XXVI" : 26, "XXVII" : 27, "XXVIII" : 28, "XXIX" : 29, "XXX" : 30, 
         "XXXI" : 31, "XXXII" : 32, "XXXIII" : 33, "XXXIV" : 34, "XXXV" : 35, "XXXVI" : 36, "XXXVII" : 37, "XXXVIII" : 38, "XXXIX" : 39, "XL" : 40,
         "XLI" : 41, "XLII" : 42, "XLIII" : 43, "XLIV" : 44, "XLV" : 45, "XLVI" : 46, "XLVII" : 47, "XLVIII" : 48, "XLIX" : 49, "L" : 50, 
         "LI" : 51, "LII" : 52, "LIII" : 53, "LIV" : 54, "LV" : 55, "LVI" : 56, "LVII" : 57, "LVIII" : 58, "LIX" : 59, "LX" : 60, 
         "LXI" : 61, "LXII" : 62, "LXIII" : 63, "" : None}
	volId, chapId = ("", "")
	
	volumnReXp=r'''\s*
               (?:VOLUME|VOL\.|BOOK)  # VOLUMN  VOL.
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
						['Gone with the wind.txt', 'gbk'],
						['pride and prejudice.txt', 'gbk'], #有录音
						['david copperfield.txt', 'utf_8_sig'],#有录音
						['Emma.txt', 'gbk'],#有录音
						['hard times.txt', 'utf_8_sig'], #有录音
						['Jane Eyre.txt', 'gbk'], #有录音
						['lord jim.txt', 'gbk'],#有录音
						['Mansfield Park.txt', 'latin_1'],#有录音
						['martin chuzzlewit.txt', 'latin_1'],#有录音
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
						['The call of the wild.txt', 'latin_1'],
						['White fang.txt', 'latin_1'],
						['The sea wolf.txt', 'latin_1'],
						['An inquiry into the nature and causes of the wealth of nations.txt',  'latin_1'],
						["A collection of english language children's literature.txt", 'latin_1'],
            ]

'''
NovelList = [
#几部最长的小说
						['Gone with the wind.txt', 'gbk'],
						['Tess of the Urbervilles.txt','gbk'],
						['The count of monte Cristo.txt','gbk'],
						['martin chuzzlewit.txt', 'latin_1'],
						['david copperfield.txt', 'utf_8_sig'],
						['sons and lovers.txt','gbk'],
						]

NovelList = [
						['The old man and the sea.txt', 'utf_8_sig'],
						['Lost Horizon.txt', 'latin_1'],
						['The Life of the Bee.txt', 'utf_8_sig'],
						['The sun also rises.txt', 'gbk'],
						['Treasure Island.txt', 'gbk'],
						['Agnes Grey.txt', 'utf_8_sig'],
						['the adventure of tom sawyer.txt', 'utf_8_sig'],
						['Northanger Abbey.txt', 'gbk'],
						['Persuasion.txt', 'gbk'],
						['the Adventures of Huckleberry Finn.txt', 'utf_8_sig'],
						['hard times.txt', 'utf_8_sig'],
						['Wuthering Heights.txt', 'gbk'],
						['the mayor of casterbridge.txt', 'gbk'],
						['sense and sensibility.txt', 'gbk'],
						['pride and prejudice.txt', 'gbk'],
						['lord jim.txt', 'gbk'],
						]
						


NovelList = [
#这个列表，按照 小说的长度从小到大排列
						['The old man and the sea.txt', 'utf_8_sig'],
						['The call of the wild.txt', 'latin_1'],
						['Lost Horizon.txt', 'latin_1'],
						['The Life of the Bee.txt', 'utf_8_sig'],
						['The sun also rises.txt', 'gbk'],
						['Treasure Island.txt', 'gbk'],
						['Agnes Grey.txt', 'utf_8_sig'],
						['the adventure of tom sawyer.txt', 'utf_8_sig'],
						['White fang.txt', 'latin_1'],
						['Northanger Abbey.txt', 'gbk'],
						['Persuasion.txt', 'gbk'],
						['the Adventures of Huckleberry Finn.txt', 'utf_8_sig'],
						['hard times.txt', 'utf_8_sig'],
						['The sea wolf.txt', 'latin_1'],
						['Wuthering Heights.txt', 'gbk'],
						['the mayor of casterbridge.txt', 'gbk'],
						['sense and sensibility.txt', 'gbk'],
						['pride and prejudice.txt', 'gbk'],
						['lord jim.txt', 'gbk'],
						['A tale of two cities.txt', 'latin_1'],
						['the return of the native.txt', 'utf_8_sig'],
						['Tess of the Urbervilles.txt', 'gbk'],
						['Sister Carrie.txt', 'gbk'],
						['sons and lovers.txt', 'gbk'],
						['Emma.txt', 'gbk'],
						['Mansfield Park.txt', 'latin_1'],
						['oliver twist.txt', 'gbk'],
						['Jane Eyre.txt', 'gbk'],
						['the moonstone.txt', 'gbk'],
						["A collection of english language children's literature.txt", 'latin_1'],
						['martin chuzzlewit.txt', 'latin_1'],
						['david copperfield.txt', 'utf_8_sig'],
						['An inquiry into the nature and causes of the wealth of nations.txt', 'latin_1'],
						['Gone with the wind.txt', 'gbk'],
						['The count of monte Cristo.txt', 'gbk'],
						]
'''


					
def chapVolId(chapId, volId = None, encoding = 0):
	if (encoding != 0):
		if (volId != None):
			return volId * 1000 + chapId
		else:
			return chapId
	else:
		volId = chapId // 1000
		chapId = chapId % 1000
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
	txtFile = open(str('C:\\GRE 词频统计\\YuLiaoKu\\') + bookName, 'rt', encoding = enc)
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
	if (re.search("G", stemmer.wordsInfo[wordPos])):
		isGre = "G"
	if (re.search("T", stemmer.wordsInfo[wordPos])):
		isTofel = "T"
	return "[" + isGre + isTofel + "]"
	
def sortByFreqAndAlphabet(wordPos1, wordPos2):
	'''先按照词性归类， 对于相同词性的单词，按照 词频排序， 在词频相同的情形下，按照字典顺序排序'''
	# use the expression (a > b) - (a < b) as the equivalent for cmp(a, b)
	freqOrder = (occurCounts[wordPos1] > occurCounts[wordPos2]) - (occurCounts[wordPos1] < occurCounts[wordPos2])
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

starttime = datetime.now()
stemmer = DictStemmer()
endtime = datetime.now()
logging.info("Stemmer initialized: %d s" % (endtime - starttime).seconds)

#本来，我是打算使用dpath.util.search的，但是发现，执行起来非常慢。所以，只能用wordOccurrence、chapContains来统计信息了。
wordOccurrence = {}  # 统计各个词 在每本书的每一章 出现的次数
bookChapWords = {}  # 统计每本书的每一章， 出现了哪些单词
for novelInfo in NovelList:
	starttime = datetime.now()
	chapContents = getChapMaps(novelInfo[0], novelInfo[1])
	bookName = re.sub(r"\.txt", "", novelInfo[0])
	print("handling %s, %d of %d" % (bookName, NovelList.index(novelInfo) + 1, len(NovelList)))
	for chapId in sorted(chapContents.keys()):
		chap = chapContents[chapId]
		sents = nltk.sent_tokenize(chap)
		for sent in sents:
			tokens = nltk.word_tokenize(sent)
			tokenPOS = nltk.pos_tag(tokens)
			logging.info(tokenPOS)
			for wordAndPos in tokenPOS:
				try:
					(word, Pos) = stemmer.doStemming(wordAndPos)
					logging.info("(%s, %s)"%(word, Pos))
					updateWordOccurence(wordOccurrence, word, Pos, bookName, chapId)
					updateBookChapWords(bookChapWords, bookName, chapId, word, Pos)
				except NoWordInDict:
					logging.error("(%s, %s) not in DICT"%(wordAndPos[0], wordAndPos[1]))
					continue
				except COCAPosInfoNotExist:
					logging.error("(%s, %s) not have POS"%(wordAndPos[0], wordAndPos[1]))
					continue
				except SkipThisWord:
					logging.info("(%s, ---)" % wordAndPos[0])
					continue
	endtime = datetime.now()
	logging.info("Handing novel <%s>: %d s" % (bookName, (endtime - starttime).seconds))

occurCounts = {}
for word in wordOccurrence:
	for Pos in wordOccurrence[word]:
		occurCounts[word+"$"+Pos] = sum(enumerateDic(wordOccurrence[word][Pos]))


wordPosInterested = set(wordPos for wordPos in stemmer.wordsInfo if re.search("G|T", stemmer.wordsInfo[wordPos]))
wordsInterested = set(re.split(r"[$]", wordPos)[0] for wordPos in wordPosInterested)

#打印各个书的章节中的词（按照字母顺序）
logging.critical("-------------- Print words according to alphabet order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	for chap in sorted(bookChapWords[bookName]):
		logging.critical("--------------------------------------\n  %s,  Chapter %s \n--------------------------------------" % (bookName, chapVolId(chap)))
		wordsToPrint =  set(wordPos for wordPos in bookChapWords[bookName][chap])  & wordPosInterested
		if (len(wordsToPrint) == 0):
			continue
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
		for wordPos in sorted(wordsToPrint):
			word, Pos = re.split(r"[$]", wordPos)
			logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的章节中的词（按照词频顺序，最少出现词最先打印）
logging.critical("-------------- Print words according to word frequency order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	for chap in sorted(bookChapWords[bookName]):
		logging.critical("--------------------------------------\n  %s,  Chapter %s \n--------------------------------------" % (bookName, chapVolId(chap)))
		wordsToPrint =  set(wordPos for wordPos in bookChapWords[bookName][chap])  & wordPosInterested
		if (len(wordsToPrint) == 0):
			continue
		maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
		for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet)):
			word, Pos = re.split(r"[$]", wordPos)
			logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的单词（按照字母顺序）
logging.critical("-------------- Book word summary, print words according to alphabet order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	logging.critical("--------------------------------------\n  <%s> word summary (alphabet order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	if (len(wordsToPrint) == 0):
		continue
	maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
	for wordPos in sorted(wordsToPrint):
		word, Pos = re.split(r"[$]", wordPos)
		#occurChaps = list(chapVolId(chapVol) for chapVol in sorted(wordOccurrence[word][Pos][bookName]))
		occurChaps = genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))
		logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d,%-2d] %s [%s]", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], ','.join(occurChaps))
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的单词（按照词频顺序，最少出现词最先打印）
logging.critical("-------------- Book word summary, print words according to word frequency order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	logging.critical("--------------------------------------\n  <%s> word summary (word frequency order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	if (len(wordsToPrint) == 0):
		continue
	maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
	for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet)):
		word, Pos = re.split(r"[$]", wordPos)
		occurChaps = genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))
		logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d,%-2d]  %s [%s]", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], ','.join(occurChaps))
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#按照单词，打印各个单词出现在各本书的名称
logging.critical("-------------- Word Summary, print words according to alphabet order ------------------------")
starttime = datetime.now()
wordsToPrint = set(word+"$"+Pos for word in wordOccurrence for Pos in wordOccurrence[word]) & wordPosInterested
maxWordLen = max(len(re.split(r"[$]", wordPos)[0]) for wordPos in wordsToPrint)
for wordPos in sorted(wordsToPrint):
	word, Pos = re.split(r"[$]", wordPos)
	bookOccurInfo = ""
	for bookName in wordOccurrence[word][Pos]:
		#bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), ','.join(genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))))
		bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])))
	logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d] %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], stemmer.WordsMeaning[wordPos], bookOccurInfo)
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

logging.critical("-------------- Word Summary, print words according to frequency order ------------------------")
starttime = datetime.now()
for wordPos in sorted(wordsToPrint, key = cmp_to_key(sortByFreqAndAlphabet)):
	word, Pos = re.split(r"[$]", wordPos)
	bookOccurInfo = ""
	for bookName in wordOccurrence[word][Pos]:
		#bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), ','.join(genCompactChaps(sorted(wordOccurrence[word][Pos][bookName]))))
		bookOccurInfo += "%s[%s] " % (cmprssBookName(bookName), sum(enumerateDic(wordOccurrence[word][Pos][bookName])))
	logging.critical("%-" + str(maxWordLen+3) + "s%2s%5s [%-2d] %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], stemmer.WordsMeaning[wordPos], bookOccurInfo)
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)


# 计算出现的词汇，占GRE词汇的覆盖率
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
		logging.critical("(%s, %s)  %.2f%%" % (bookName, chapVolId(chap), len(wordPosInNovel[bookName])/len(wordPosInterested)*100))
	logging.critical("wordPos %s %.2f%%" % (bookName, len(wordPosInNovels) / len(wordPosInterested)*100))
	wordsInNovels = set(re.split(r"[$]", wordPos)[0] for wordPos in wordPosInNovels)
	logging.critical("word %s %.2f%%" % (bookName, len(wordsInNovels) / len(wordsInterested)*100))


books = [book for book in wordPosInNovel.keys()]

logging.critical("words intersection relationship: (book1, book2) = (wordset1, wordset2, wordset1 & wordset2, wordset1 | wordset2)")
result = []
for (book1, book2) in itertools.combinations(books, 2):
	result.append((book1, book2, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                         len(wordPosInNovel[book2])/len(wordPosInterested)*100, 
	                         len(wordPosInNovel[book1] & wordPosInNovel[book2])/len(wordPosInterested)*100,
	                         len(wordPosInNovel[book1] | wordPosInNovel[book2])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.critical("(%s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)

result.clear()
logging.critical("words intersection relationship: (book1, book2, book3) = (wordset1, wordset2, wordset3, wordset1 | wordset2 | wordset3)")
for (book1, book2, book3) in itertools.combinations(books, 3):
	result.append((book1, book2, book3, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                                    len(wordPosInNovel[book2])/len(wordPosInterested)*100,
	                                    len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
	                                    len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.critical("(%s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)
	                                                       
result.clear()
logging.critical("words intersection relationship: (book1, book2, book3, book4) = (wordset1, wordset2, wordset3, wordset4, wordset1 | wordset2 | wordset3 | wordset4)")
for (book1, book2, book3, book4) in itertools.combinations(books, 4):
	result.append((book1, book2, book3, book4,
                                    len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
                                    len(wordPosInNovel[book2])/len(wordPosInterested)*100,
                                    len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
                                    len(wordPosInNovel[book4])/len(wordPosInterested)*100, 
	                                  len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3] | wordPosInNovel[book4])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.critical("(%s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item )
	
	
result.clear()
logging.critical("words intersection relationship: (book1, book2, book3, book4, book5) = (wordset1, wordset2, wordset3, wordset4, wordset5, wordset1 | wordset2 | wordset3 | wordset4 |wordset5)")
for (book1, book2, book3, book4, book5) in itertools.combinations(books, 5):
	result.append((book1, book2, book3, book4, book5, len(wordPosInNovel[book1])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book2])/len(wordPosInterested)*100,
	                   len(wordPosInNovel[book3])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book4])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book5])/len(wordPosInterested)*100, 
	                   len(wordPosInNovel[book1] | wordPosInNovel[book2] | wordPosInNovel[book3] | wordPosInNovel[book4] | wordPosInNovel[book5])/len(wordPosInterested)*100))
for item in sorted(result,  key = lambda x: x[len(x) - 1], reverse=True):
	logging.critical("(%s, %s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)

'''
result.clear()
logging.critical("words intersection relationship: (book1, book2, book3, book4, book5, book6) = (wordset1, wordset2, wordset3, wordset4, wordset5, wordset6, wordset1 | wordset2 | wordset3 | wordset4 |wordset5 | wordset6)")
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
	logging.critical("(%s, %s, %s, %s, %s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%, %.2f%%)" % item)
'''


# 哪些词在所有小说中，都没有出现过
wordsNotOccur = wordPosInterested - wordPosInNovels
logging.critical("words that don't show in any novels")
for wordPos in sorted(wordsNotOccur):
	word, Pos = re.split(r"[$]", wordPos)
	logging.critical("%-17s%2s%5s %s", word, Pos, getWordMark(wordPos), stemmer.WordsMeaning[wordPos])

