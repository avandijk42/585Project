# from lyricsFetch import lyricsFetch
import re

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
	print ngrams[0]
	print featvec[0]
	return (featvec, encoder, decoder)
