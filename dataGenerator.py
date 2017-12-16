"""
Author: Nick Laurin
This handles data generation including feature vector extraction and storage. 
"""
import lyricsFetch
import lexicalFeatureGenerator as lfg
#TODO
input_ = open("rock_abridged.txt", "r")
output_ = open("some_ngrams.txt", "w+")
#gen feature vectors
lfg.get_ngram_featvec(input_,3)

