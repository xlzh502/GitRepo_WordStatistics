# coding=gbk

import logging
import re
import nltk
from string import Template
import pdb
from DictStemmer import DictStemmer, NoWordInDict, COCAPosInfoNotExist, SkipThisWord


logging.basicConfig(format='%(levelname)s:%(message)s',  filename="c:\\GRE 词频统计\\logging.txt", filemode='w', level=logging.DEBUG)

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


'''
NovelList = [
						['Gone with the wind.txt', 'gbk'],
						['pride and prejudice.txt', 'latin_1'],
						['david copperfield.txt', 'utf-8-sig'],
						['Emma.txt', 'latin_1'],
						#['hard times.txt', 'utf-8-sig'], # 无法识别
						['Jane Eyre.txt', 'latin_1'],
						['lord jim.txt', 'latin_1'],
						['Mansfield Park.txt', 'iso8859_2'],
						#['martin chuzzlewit.txt', 'latin_1'],  # 无法识别
						['Northanger Abbey.txt', 'latin_1'],
						['oliver twist.txt', 'latin_1'],
						['Persuasion.txt', 'latin_1'],
						['sense and sensibility.txt','latin_1'],
						['Sister Carrie.txt','latin_1'],
						['sons and lovers.txt','latin_1'],
						#['Tess of the Urbervilles.txt','latin_1'],  # 无法识别
						['the adventure of tom sawyer.txt','utf_8_sig'],
						['The count of monte Cristo.txt','latin_1'],
						['The genius.txt','latin_1'],
						['the mayor of casterbridge.txt','latin_1'],
						['the moonstone.txt','latin_1'],
						['the return of the native.txt','utf_8_sig'],
						['Treasure Island.txt','latin_1'],
						['Wuthering Heights.txt','latin_1']
            ]
'''
NovelList = [
						['Gone with the wind.txt', 'gbk'],
						]

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
			for tokenAndPos in tokenPOS:
				try:
					(word, Pos) = stemmer.doStemming(tokenAndPos)
					if (word not in wordOccurrence[bookName][chapId]):
						wordOccurrence[bookName][chapId][word] = {}
						wordOccurrence[bookName][chapId][word][Pos] = 1
					else:
						wordOccurrence[bookName][chapId][word][Pos] = wordOccurrence[bookName][chapId][word].get(Pos, 0) + 1
				except NoWordInDict:
					continue
				except COCAPosInfoNotExist:
					continue
				except SkipThisWord:
					continue
										
					
