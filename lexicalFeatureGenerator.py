# from lyricsFetch import lyricsFetch
import re
from nltk.corpus import cmudict
import time
import numpy as np
import os

cmud = cmudict.dict()
cmuw = cmudict.words()
vowels = ['AA', 'AH', 'AW', 'EH', 'EY', 'IH', 'OW', 'UH', 'AE', 'AO', 'AY', 'ER', 'IY', 'OY', 'UW']
fixed = {}
rhyme2words = {}

def get_lyric_ngrams(artistCount,songCount,category='rock',ngram=3):
	lf = lyricsFetch('rock', artistCount, songCount)

	lyrics = []
	for i in range(artistCount-1):
		lyrics.append(lf.getNextLyricSet()[2])

	allLines = []
	for l in lyrics:
		lines_str = re.sub('\n\n', '\n', l)
		lines = lines_str.split('\n')
		lines = [re.sub(r'([,!?]|\.{3})', r' \1', x) for x in lines]
		for li in lines:
			allLines.append(li)
	return get_ngrams(allLines, ngram)

# given a list of lines, returns a flattened list of ngrams, including start and stop tokens
# if n > len(line) + 2, it will return [<START>] + line + [<STOP>]
def get_ngrams(lines, n):
	ngrams = []
	for line in lines:
		line_formatted = ['<S_L>'] + line.split() + ['<E_L>']
		if len(line) < n-1:
			ngrams.append(line_formatted)
		else:
			# expression for the number of ngrams in a sequence
			num_ngram = len(line_formatted) - n + 1
			for i in range(num_ngram):
				ngrams.append(line_formatted[i:i+n])
	return ngrams

def get_ngrams_normalized(text, n):
	text = re.sub('[\[\]!?().,":;]', '', text) # strip bad characters
	songs = text.split('\n\n<SONG_BOUNDARY>\n\n')
	lines = [line for song in songs for stanza in song.split('\n\n') for line in stanza.split('\n')]
	ngrams = []
	for line in lines:
		line_formatted = [w.lower() for w in line.split()]
		line_formatted.append('<endline>')
		if len(line) < n-1:
			ngrams.append(line_formatted)
		else:
			# expression for the number of ngrams in a sequence
			num_ngram = len(line_formatted) - n + 1
			for i in range(num_ngram):
				ngrams.append(line_formatted[i:i+n])
	return ngrams

def get_ngram_strings(lines, n):
	ngrams = []
	for line in lines:
		line_formatted = '<S_L> ' + line + ' <E_L>'
		if len(line_formatted.split()) <= n:
			ngrams.append(line_formatted)
		else:
			# expression for the number of ngrams in a sequence
			num_ngram = len(line_formatted.split()) - n + 1
			tokens = line_formatted.split()
			for i in range(num_ngram):
				ngram = tokens[i]
				for token in tokens[i+1:i+n]:
					ngram = ngram + ' ' + token
				ngrams.append(ngram)
				
	return ngrams

# takes in formatted lyric text in the form of "[line]\n[line]\n...[line]\n\n<SONG_BOUNDARY>\n\n..."
def get_ngram_featvec(text, n):
	lines = [line for song in text.split("\n\n<SONG_BOUNDARY>\n\n") for lines in song.split('\n\n') for line in lines.split('\n')]
	ngrams = get_ngram_strings(lines, n)
	unique = list(set(ngrams))
	print str(n)+'-gram feature vector has '+str(len(unique))+' dimensions'
	encoder = {v:i for i,v in enumerate(unique)}
	decoder = {i:v for i,v in enumerate(unique)}
	featvec = [encoder[ngram] for ngram in ngrams]
	return featvec, encoder, decoder

def getRhymePhonemes(word):
	nonum = lambda x: re.sub('\d', '', x)
	w = re.sub('[!?().,":;]', '', word)
	w = w.lower()
	if w in cmuw:
		prons = cmud[w]
		rhymes = []
		for pron in prons:
			if nonum(pron[-1]) in vowels:
				rhymes.append([nonum(pron[-1])])
			else:
				rhymes.append([nonum(phoneme) for phoneme in pron[-2:]])
		return rhymes
	if re.match('.*in\'$', word):
		w = re.sub('in\'', 'ing', w)
		if w in cmuw:
			prons = cmud[w]
			rhyme = []
			for pron in prons:
				if pron[-1] == "NG":
					rhyme.append([nonum(pron[-2]), 'N'])
			return rhyme
	if word.lower() in fixed.keys():
		return [[fixed[word.lower()]]]
	return [['X']]

def stanzaRhymePattern(L):
	C = ['']*len(L)
	for i,p in enumerate(L):
		if p == ['X']:
			C[i] = 'X'

	cur = 0
	for i,p1 in enumerate(L):
		if C[i] == '':
			C[i] = cur
			for j in range(i+1, len(L)):
				p2 = L[j]
				if len(set(p1) & set(p2)) > 0:
					C[j] = cur
			cur += 1
	ret = ''
	for x in C:
		ret = ret + str(x) + ' '
	return ret[:-1]

def phonListToStr(phonList):
	string = ""
	for i,p in enumerate(phonList):
		if i == len(phonList)-1:
			string = string + p
		else:
			string += string + p + ' '
	return string

def rhyme_pattern(song):
	stanzas = song.split('\n\n')
	pattern = ''
	for st in stanzas:
		lastWords = [l.split(' ')[-1] for l in st.split('\n')]
		L = [list(set([phonListToStr(s) for s in getRhymePhonemes(w)])) for w in lastWords]
		pattern = pattern + stanzaRhymePattern(L) + ','
	return '<RH=' + pattern[:-1] + '>'

def populateOutwords():
	f = open("rock.txt", 'r')
	out = open("outwords.txt", 'w')
	i = 0
	for song in open("rock.txt", 'r').read().split('\n\n<SONG_BOUNDARY>\n\n'):
		song = re.sub(' +\n', '\n', song)
		for stanza in song.split('\n\n'):
			for line in stanza.split('\n'):
				last = line.split(' ')[-1]
				last = re.sub('[!?().,":;]', '', last)
				if re.match('.*in\'$', last):
					last = re.sub('in\'', 'ing', last)
				if last.lower() not in cmuw:
					out.write(last.lower() + '\n')
				if i % 100 == 0:
					print i
				i += 1
	f.close()
	out.close()

def processFixed():
	f = open("fixed.txt", 'r')
	for word in f.read().split('\n'):
		x = word.split('|')
		if len(x[1]) > 0:
			fixed[x[0]] = x[1]
		else:
			continue


def generatePatterns(genre):
	f = open("%s.txt" % (genre), 'r')
	processFixed()

	patterns = open("patterns.txt", 'w')

	songs = f.read().split('\n\n<SONG_BOUNDARY>\n\n')

	# start = time.time()
	for i,s in enumerate(songs):
		if i%50==0: print i/len(songs),'%'
		s = re.sub(' \n', '\n', s)
		rhyme = rhyme_pattern(s)
		rhyme = re.sub('<RH=', '', rhyme)
		rhyme = re.sub('>', '', rhyme)
		rstanza = rhyme.split(',')
		for rhymePattern in rstanza:
			if 'X' in rhymePattern: continue
			if max([int(r) for r in rhymePattern.split(' ')]) < 6:
				patterns.write(rhymePattern + '\n')


generatePatterns('rock')
# N = 4

# ngrams = [tuple(x) for x in get_ngrams_normalized(f.read(),N)]
# lasts = [ngram for ngram in ngrams if list(ngram)[-1] == '<endline>']
# from gauss import backGenLine

# for _ in range(20):
# 	arr = backGenLine(ngrams, np.random.choice(lasts,size=1)[0][N-2], 10)
# 	string = ""
# 	for a in arr:
# 		string = string + a + ' '
# 	print string[:-1]

# print "TOOK: " + str(time.time() - start) + ' seconds'
