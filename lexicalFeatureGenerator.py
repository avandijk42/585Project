from lyricsFetch import lyricsFetch
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
