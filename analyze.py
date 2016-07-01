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
						['pride and prejudice.txt', 'gbk'],
						['david copperfield.txt', 'utf_8_sig'],
						['Emma.txt', 'gbk'],
						['hard times.txt', 'utf_8_sig'], 
						['Jane Eyre.txt', 'gbk'],
						['lord jim.txt', 'gbk'],
						['Mansfield Park.txt', 'latin_1'],
						['martin chuzzlewit.txt', 'latin_1'],
						['Northanger Abbey.txt', 'gbk'],
						['oliver twist.txt', 'gbk'],
						['Persuasion.txt', 'gbk'],
						['sense and sensibility.txt','gbk'],
						['Sister Carrie.txt','gbk'],
						['sons and lovers.txt','gbk'],
						['Tess of the Urbervilles.txt','gbk'],
						['the adventure of tom sawyer.txt','utf_8_sig'],
						['The count of monte Cristo.txt','gbk'],
						['The genius.txt','gbk'],
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
            ]


NovelList = [
						['Mansfield Park.txt', 'latin_1'],
						['Agnes Grey.txt', 'utf_8_sig'],
						]


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
		for wordPos in sorted(wordsToPrint):
			word, Pos = re.split(r"[$]", wordPos)
			logging.critical("%-27s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的章节中的词（按照词频顺序，最少出现词最先打印）
logging.critical("-------------- Print words according to word frequency order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	for chap in sorted(bookChapWords[bookName]):
		logging.critical("--------------------------------------\n  %s,  Chapter %s \n--------------------------------------" % (bookName, chapVolId(chap)))
		wordsToPrint =  set(wordPos for wordPos in bookChapWords[bookName][chap])  & wordPosInterested
		for wordPos in sorted(wordsToPrint, key = occurCounts.__getitem__):
			word, Pos = re.split(r"[$]", wordPos)
			logging.critical("%-27s%2s%5s [%-3d,%-3d,%-3d]  %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), wordOccurrence[word][Pos][bookName][chap] ,stemmer.WordsMeaning[wordPos])
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的单词（按照字母顺序）
logging.critical("-------------- Book word summary, print words according to alphabet order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	logging.critical("--------------------------------------\n  <<%s>> word summary (alphabet order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	for wordPos in sorted(wordsToPrint):
		word, Pos = re.split(r"[$]", wordPos)
		occurChaps = list(chapVolId(chapVol) for chapVol in sorted(wordOccurrence[word][Pos][bookName]))
		logging.critical("%-27s%2s%5s [%-3d,%-3d] %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], occurChaps)
endtime = datetime.now()
logging.info("Printing word result: %d s" % (endtime - starttime).seconds)

#打印各个书的单词（按照词频顺序，最少出现词最先打印）
logging.critical("-------------- Book word summary, print words according to word frequency order ------------------------")
starttime = datetime.now()
for bookName in bookChapWords:
	logging.critical("--------------------------------------\n  <<%s>> word summary (word frequency order) \n--------------------------------------" % bookName)
	wordsToPrint = set(wordPos for chap in bookChapWords[bookName] for wordPos in bookChapWords[bookName][chap]) & wordPosInterested
	for wordPos in sorted(wordsToPrint, key = occurCounts.__getitem__):
		word, Pos = re.split(r"[$]", wordPos)
		occurChaps = list(chapVolId(chapVol) for chapVol in sorted(wordOccurrence[word][Pos][bookName]))
		logging.critical("%-27s%2s%5s [%-3d,%-3d]  %s %s", word, Pos, getWordMark(wordPos), occurCounts[wordPos], sum(enumerateDic(wordOccurrence[word][Pos][bookName])), stemmer.WordsMeaning[wordPos], occurChaps)
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


logging.critical("words intersection relationship: (novel1, novel2) = (wordset1, wordset2, wordset1 | wordset2, wordset1 & wordset2)")
books = [book for book in wordPosInNovel.keys()]
wordPosSet = [info for info in wordPosInNovel.values()]
for i in range(len(books)):
	for j in range(i+1, len(books)):
		book_1 = books[i]
		book_2 = books[j]
		logging.critical("(%s, %s) = (%.2f%%, %.2f%%, %.2f%%, %.2f%%)" % (book_1, 
																															book_2,
																														  len(wordPosSet[i])/len(wordPosInterested)*100,
																														  len(wordPosSet[j])/len(wordPosInterested)*100,
																														  len(wordPosSet[i] | wordPosSet[j])/len(wordPosInterested)*100,
																														  len(wordPosSet[i] & wordPosSet[j])/len(wordPosInterested)*100))
																														  

# 哪些词在所有小说中，都没有出现过
wordsNotOccur = wordPosInterested - wordPosInNovels
logging.critical("words that don't show in any novels")
for wordPos in sorted(wordsNotOccur):
	word, Pos = re.split(r"[$]", wordPos)
	logging.critical("%-30s%s" % (word, Pos))

