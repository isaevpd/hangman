import urllib.parse as urlparse
import os
import psycopg2
from peewee import *
from playhouse.migrate import *
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
    nickname = CharField(max_length=256)

    class Meta:
        database = db

class word_created(Model):
    word = CharField(max_length=256)
    language = CharField(max_length=10)
    user = ForeignKeyField(user)

    class Meta:
        database = db


class Game(Model):
    '''
    '''
    user_identifier = FloatField(unique=True)
    word = CharField(max_length=256)
    word_length = IntegerField()
    result = CharField(max_length=15, default='in_progress')

    class Meta:
        database = db

    @classmethod
    def create_game(cls, word, user_identifier):
        '''
        '''
        cls.create(word=word, user_identifier=user_identifier,result='in_p')

class LetterGuessed(Model):
    '''
    '''
    game_id = ForeignKeyField(Game, related_name='letters')
    letter = CharField(max_length=1)
    state = CharField(max_length=500)


    class Meta:
        database = db

db.get_conn()
db.create_tables([LetterGuessed], safe=True)

aa = Game.update(result='won').where(Game.word == 'rejoined')
aa.execute()
