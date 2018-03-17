import datetime
import uuid

from mongoengine import connect, Document, EmbeddedDocument
from mongoengine.fields import (
    UUIDField,
    StringField,
    IntField,
    DateTimeField,
    EmbeddedDocumentListField
)

MIN_WORD_LENGTH = 1
MAX_WORD_LENGTH = 32
MAX_ATTEMPTS = 8


STATUS_IN_PROGRESS = 'in_progress'
STATUS_WON = 'won'
STATUS_LOST = 'lost'

STATUS_CHOICES = (
    STATUS_IN_PROGRESS,
    STATUS_WON,
    STATUS_LOST
)

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

    @property
    def word_length(self):
        return len(self.word)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.datetime.utcnow()


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
