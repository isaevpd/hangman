import urllib.parse as urlparse
import os
import psycopg2
from peewee import *
from hangman import loadWords, chooseWord
import time


# URL = urlparse.urlparse(os.environ['DATABASE_URL'])
# DBNAME = URL.path[1:]
# USER = URL.username
# PASSWORD = URL.password
# HOST = URL.hostname
# PORT = URL.port

db = PostgresqlDatabase(
    'local_db',
    user='germaniakovlev',
    password='',
    host='localhost'
)


class Result(Model):
    '''
    Creates Result table
    '''
    word = CharField(max_length=256)
    attempts = IntegerField()
    result = BooleanField()

    class Meta:
        database = db


class user(Model):
    nickname = CharField(max_length=256, unique=True)

    class Meta:
        database = db

    @classmethod
    def create_user(cls, nickname):
        try:
            cls.create(nickname=nickname)
        except IntegrityError:
            raise ValueError('User already exists')


class word_created(Model):
    word = CharField(max_length=256)
    language = CharField(max_length=10)
    #create_time = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(user)

    class Meta:
        database = db


class Letter(Model):
    '''
    Contains letters submitted by user during the game
    '''
    letter = CharField(max_length=1, unique=True)

    class Meta:
        database = db


class Game(Model):
    '''
    '''
    game_uuid = UUIDField(unique=True)
    word = CharField(max_length=256)
    word_length = IntegerField()
    result = CharField(max_length=10, default='in_progress')

    class Meta:
        database = db

    @classmethod
    def create_game(cls, game_uuid, word, word_length):
        '''
        '''
        cls.create(game_uuid=game_uuid,
                   word=word, word_length=word_length)


class LetterGuessed(Model):
    '''
    '''
    game_id = ForeignKeyField(Game, related_name='letters')
    letter = CharField(max_length=1)
    state = CharField(max_length=500)

    class Meta:
        database = db


def create_result(word, attempts, result):
    '''
    Creates an entry with the game result
    '''
    Result.create(word=word, attempts=attempts, result=result)


def create_word(word, user_id):
    word_created.create(word=word, user=user_id, language='')
