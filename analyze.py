# coding=gbk

import logging
import re
import nltk
from string import Template
import pdb
from DictStemmer import DictStemmer, NoWordInDict, COCAPosInfoNotExist, SkipThisWord
import dpath.util


#logging.basicConfig(format='%(levelname)s:%(message)s',  filename="c:\\GRE 词频统计\\logging.txt", filemode='w', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s',  filename="c:\\GRE 词频统计\\logging.txt", filemode='w', level=logging.CRITICAL)

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
						['david copperfield.txt', 'utf-8-sig'],
						['Emma.txt', 'gbk'],
						#['hard times.txt', 'utf-8-sig'], # 无法识别
						['Jane Eyre.txt', 'gbk'],
						['lord jim.txt', 'gbk'],
						['Mansfield Park.txt', 'iso8859_2'],
						#['martin chuzzlewit.txt', 'latin_1'],  # 无法识别
						['Northanger Abbey.txt', 'gbk'],
						['oliver twist.txt', 'gbk'],
						['Persuasion.txt', 'gbk'],
						['sense and sensibility.txt','gbk'],
						['Sister Carrie.txt','gbk'],
						['sons and lovers.txt','gbk'],
						#['Tess of the Urbervilles.txt','gbk'],  # 无法识别
						['the adventure of tom sawyer.txt','utf_8_sig'],
						['The count of monte Cristo.txt','gbk'],
						['The genius.txt','gbk'],
						['the mayor of casterbridge.txt','gbk'],
						['the moonstone.txt','gbk'],
						['the return of the native.txt','utf_8_sig'],
						['Treasure Island.txt','gbk'],
						['Wuthering Heights.txt','gbk']
            ]

'''NovelList = [
						['Gone with the wind.txt', 'gbk'],
						]
'''
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
				chapContents[float(str(lastVolId) + '.' + str(lastChapId))] = chap
			else:
				chapContents[lastChapId] = chap
		else:
			continue
	return chapContents
	
	



#stemmer = DictStemmer()
#outputFile.write("volId={}, chapId=P{}\n".format(lastVolId, lastChapId))
#			sents = nltk.sent_tokenize(chap)
#			for sent in sents:
#				tokens = nltk.word_tokenize(sent)
#				tokenPOS = nltk.pos_tag(tokens)
#				outputFile.write(str(tokenPOS))
#				outputFile.write("\n")



stemmer = DictStemmer()
wordOccurrence = {}
for novelInfo in NovelList:
	chapContents = getChapMaps(novelInfo[0], novelInfo[1])
	bookName = re.sub(r"\.txt", "", novelInfo[0])
	wordOccurrence[bookName] = {}
	for chapId in sorted(chapContents.keys()):
		wordOccurrence[bookName][chapId] = {}
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
					if (word not in wordOccurrence[bookName][chapId]):
						wordOccurrence[bookName][chapId][word] = {}
						wordOccurrence[bookName][chapId][word][Pos] = 1
					else:
						wordOccurrence[bookName][chapId][word][Pos] = wordOccurrence[bookName][chapId][word].get(Pos, 0) + 1
				except NoWordInDict:
					logging.error("(%s, %s) not in DICT"%(wordAndPos[0], wordAndPos[1]))
					continue
				except COCAPosInfoNotExist:
					logging.error("(%s, %s) not have POS"%(wordAndPos[0], wordAndPos[1]))
					continue
				except SkipThisWord:
					logging.info("(%s, ---)" % wordAndPos[0])
					continue

wordsToPrint = ['ignominious','wiggle', 'vicious', 'semblance', 'eloquence', 'listless', 'morose', 'grumble', 'appetite', 'scowl', 'tactics', 'shuffle','stubborn', 'disposition','jealous','ignominious']
for word in wordsToPrint:
	result = dpath.util.search(wordOccurrence, "/*/*/" + word + "/*")
	print(result)
