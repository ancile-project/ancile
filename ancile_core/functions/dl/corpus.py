import os
from io import open
import torch


class Dictionary(object):
    def __init__(self):
        self.word2idx = {}
        self.idx2word = []
        self.add_word("eos")

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        return self.word2idx[word]

    def __len__(self):
        return len(self.idx2word)


class Corpus(object):
    def __init__(self, dates):
        self.dictionary = Dictionary()
        train_dates = {k: v for k, v in dates.items() if k[0] != 6}
        test_dates = {k: v for k, v in dates.items() if k[0] == 6}
        self.train = self.tokenize(train_dates)
        self.test = self.tokenize(test_dates)

    def tokenize(self, dates):
        """Tokenizes a text file."""
        count = 0
        for values in dates.values():
            for value in values:
                self.dictionary.add_word(value)
                count += 1
            count += 1
        ids = torch.LongTensor(count)
        count = 0
        for x, values in sorted(dates.items(), key=lambda x: x[0]):
            for value in values:
                ids[count] = self.dictionary.word2idx[value]
                count += 1
            ids[count] = 0
            count += 1
        print(len(self.dictionary.idx2word))

        return ids