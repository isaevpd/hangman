import random

WORDLIST_FILENAME = 'words.txt'


def choose_word():
    with open(WORDLIST_FILENAME) as word_list:
        return random.choice(word_list.readline().split())
