from __future__ import division
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt

def pickN(distro, n=10):
	w = {}
	for x in distro:
		if x not in w:
			w[x] = 1
		else:
			w[x] += 1
	total = sum(w.values())
	w = {k:v/total for k,v in w.items()}
	return np.random.choice(w.keys(), size=n, p=w.values())

def calcCDF():
	s = np.random.normal(0,0.1,10000)
	count,bins,_ = plt.hist(s,100,normed=True)
	print count[:20]
	plt.plot(range(count), np.cumsum(bins[:-1]) - min(bins))

def backGenLine(allNgrams, seed, lineLength = 10): # returns generated line
	# make dict of ngrams to their counts
	w = {}
	n = len(allNgrams[0])
	for ngram in allNgrams:
		if ngram not in w:
			w[ngram] = 1
		else:
			w[ngram] += 1

	# grab ngram:count entries whose last token is the seed word
	lastCandidates = {ngram:count for ngram,count in w.items() if seed in ngram and ngram.index(seed) == n-1}
	
	# utility function to format ngrams for use in np.random.choice
	def strFlatten(tup):
		toReturn = ""
		for x in list(tup):
			toReturn += str(x) + ' '
		return toReturn[:-1]

	flatCandidates = [(strFlatten(x),w[x]) for x in lastCandidates.keys()]

	# make a probability distribution proportional to the counts of each ngram
	if len(flatCandidates) == 0:
		return None
	probs = np.array([y for x,y in flatCandidates]) / sum(lastCandidates.values())
	# # amplify probability distribution
	# probs = (probs + ((max(probs) - min(probs)) / 2)) ** 2
	# probs = probs / sum(probs)
	# randomly select ngram with probability proportional to their counts
	last = np.random.choice([x for x,y in flatCandidates], p=probs, size=1)

	overlap = lambda x,y: x[1:] == y[:n-1]
	build = last[0].split()
	for _ in range(lineLength-n):
		candidates = {ngram:count for ngram,count in w.items() if overlap(list(ngram),build)}
		if len(candidates) == 0:
			return build
		flatCandidates = [(strFlatten(x),y) for x,y in candidates.items()]
		probs = np.array([y for x,y in flatCandidates]) / sum(candidates.values())
		best = np.random.choice([x for x,y in flatCandidates], p=probs, size=1)[0]
		build.insert(0, best.split()[0])
	return build