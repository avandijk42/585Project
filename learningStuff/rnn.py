import numpy as np
from lexicalFeatureGenerator import getRhymeFeatVec

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Convolution2D, Permute, LSTM, TimeDistributed
from keras.utils.np_utils import to_categorical
#data = open('lyrics.txt')
# with open('patterns.txt') as f:
#     mylist = [line.rstrip('\n') for line in f]
# print (len(mylist))
# chars = list(set(mylist))
mylist, char_to_ix, ix_to_char = getRhymeFeatVec()
chars = list(char_to_ix.keys())

VOCAB_SIZE = len(chars)
SEQ_LENGTH = 6


# ix_to_char = {ix:char for ix, char in enumerate(chars)}
# char_to_ix = {char:ix for ix, char in enumerate(chars)}

"""
3 dimensions for the figure.

The number of features is the 3rd dimension. This is the list of the chars set because we are using the characters
as features

The length of the sequence is how many characters we want the model to look at a time. We chose 6 so that it looks
at every word

The number of sequences is the amount of data / the sequences we want looked at for each time

"""
X = np.zeros((int(len(mylist)/SEQ_LENGTH), SEQ_LENGTH, len(chars)))
y = np.zeros((int(len(mylist)/SEQ_LENGTH), SEQ_LENGTH, len(chars)))
for i in range(0, int(len(mylist)/SEQ_LENGTH)):
    X_sequence = mylist[i*SEQ_LENGTH:(i+1)*SEQ_LENGTH]
    X_sequence_ix = [char_to_ix[value] for value in X_sequence]
    input_sequence = np.zeros((SEQ_LENGTH, VOCAB_SIZE))
    for j in range(SEQ_LENGTH):
        input_sequence[j][X_sequence_ix[j]] = 1.
    X[i] = input_sequence

    y_sequence = mylist[i*SEQ_LENGTH+1:(i+1)*SEQ_LENGTH+1]
    y_sequence_ix = [char_to_ix[value] for value in y_sequence]
    target_sequence = np.zeros((SEQ_LENGTH, VOCAB_SIZE))
    for j in range(SEQ_LENGTH):
        target_sequence[j][y_sequence_ix[j]] = 1.
    y[i] = target_sequence


model = Sequential()
HIDDEN_DIM = 3
LAYER_NUM = 3
model.add(LSTM(HIDDEN_DIM, input_shape=(None, VOCAB_SIZE), return_sequences=True))
for i in range(LAYER_NUM - 1):
    model.add(LSTM(HIDDEN_DIM, return_sequences=True))
model.add(TimeDistributed(Dense(VOCAB_SIZE)))
model.add(Activation('softmax'))
model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

def generate_text(model, length):
    ix = [np.random.randint(VOCAB_SIZE)]
    y_char = [ix_to_char[ix[-1]]]
    X = np.zeros((1, length, VOCAB_SIZE))
    for i in range(length):
        X[0, i, :][ix[-1]] = 1
        #print(ix_to_char[ix[-1]], end="")
        ix = np.argmax(model.predict(X[:, :i+1, :])[0], 1)
        y_char.append(ix_to_char[ix[-1]])
    return ('').join(y_char)

nb_epoch = 20
BATCH_SIZE = 5
GENERATE_LENGTH = 10
fileBad = open("badLyrics.txt", "w")

#y_binary = to_categorical(y)


while True:
    print('\n\n')
    model.fit(X, y, batch_size=BATCH_SIZE, verbose=1, nb_epoch=20)
    nb_epoch += 1
    #print(generate_text(model, GENERATE_LENGTH))
    #print('!!!!!!!!!')
    fileBad.write(generate_text(model, GENERATE_LENGTH))
    fileBad.write('\n')
    fileBad.write('!!!!!!!!!!!!!!!!!!!!!!!!!')
    fileBad.write('\n')
    #fileBad.write('test')

    if nb_epoch % 10 == 0:
        model.save_weights('checkpoint_{}_epoch_{}.hdf5'.format(HIDDEN_DIM, nb_epoch))
fileBad.close()
