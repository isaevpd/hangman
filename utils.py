import random

WORDLIST_FILENAME = 'words.txt'


def load_words():
    return open(WORDLIST_FILENAME).readline().split()


def choose_word(word_list):
    return random.choice(word_list)
