import datetime
import string
import uuid
import os

from mongoengine import connect, Document, EmbeddedDocument
from mongoengine.fields import (
    UUIDField,
    StringField,
    IntField,
    DateTimeField,
    EmbeddedDocumentListField
)

from constants import (
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
    MAX_ATTEMPTS,
    STATUS_IN_PROGRESS,
    STATUS_WON,
    STATUS_LOST,
    STATUS_CHOICES
)

try:
    connect(
        host=os.environ['MONGODB_URI']
    )
except KeyError:
    connect('hangman')


class Game(Document):
    uuid = UUIDField(unique=True, required=True, default=uuid.uuid4)
    word = StringField(
        regex=f'^[a-z]{{{MIN_WORD_LENGTH},{MAX_WORD_LENGTH}}}$',
        required=True
    )
    status = StringField(
        min_length=3,
        max_length=16,
        default=STATUS_IN_PROGRESS,
        choices=STATUS_CHOICES
    )
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    letters = EmbeddedDocumentListField('LetterGuessed')

    def __str__(self):
        return (
            f'{self.uuid}->{self.word}->{self.status}'
        )

    @classmethod
    def pre_save(cls, sender, game, **kwargs):
        game.updated_at = datetime.datetime.utcnow()
        # update game status if needed
        if not game.is_over:
            if game.representation == game.word:
                game.status = STATUS_WON

            elif game.last_letter.attempts_left == 0:
                game.status = STATUS_LOST

    @property
    def word_length(self):
        return len(self.word)

    @property
    def letters_guessed(self):
        return {l.letter for l in self.letters}

    @property
    def is_over(self):
        return self.status != STATUS_IN_PROGRESS

    @property
    def last_letter(self):
        return self.letters[-1]

    @property
    def representation(self):
        return ''.join(map(
            lambda l: l if l in self.letters_guessed else '_',
            self.word
        ))

    def get_available_letters(self, letters_guessed=None):
        if letters_guessed is None:
            letters_guessed = self.letters_guessed

        return ''.join(map(
            lambda l: l if l not in letters_guessed else '',
            string.ascii_lowercase
        ))

    def append_letter(self, letter, attempts_left, message):
        letter = LetterGuessed(
            letter=letter,
            attempts_left=attempts_left,
            message=message
        )
        self.letters.append(letter)
        self.save()
        return letter


class LetterGuessed(EmbeddedDocument):
    letter = StringField(min_length=1, max_length=1, required=True)
    attempts_left = IntField(
        min_value=0, max_value=MAX_ATTEMPTS, required=True
    )
    message = StringField(max_length=128, required=True)

    def __str__(self):
        return (
            f'{self.letter}->{self.attempts_left}->{self.message}'
        )


class CustomWord(Document):
    word = StringField(
        regex=f'^[a-z]{{{MIN_WORD_LENGTH},{MAX_WORD_LENGTH}}}$',
        required=True
    )
    uuid = UUIDField(unique=True, required=True, default=uuid.uuid4)
