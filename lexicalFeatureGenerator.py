from lyricsFetch import lyricsFetch
import re

num = 10
lf = lyricsFetch('rock', num, 5)

lyrics = []
for i in range(num-1):
	lyrics.append(lf.getNextLyricSet()[2])

allLines = []
for l in lyrics:
	lines_str = re.sub('\n\n', '\n', l)
	lines = lines_str.split('\n')
	lines = [re.sub(r'([,!?])', r' \1', x) for x in lines]
	for li in lines:
		allLines.append(li)

print allLines[:10]