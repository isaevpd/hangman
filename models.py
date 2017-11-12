import urllib.parse as urlparse
import os
import psycopg2
from peewee import *
from hangman import loadWords, chooseWord
import time
from datetime import datetime


URL = urlparse.urlparse(os.environ['DATABASE_URL'])
DBNAME = URL.path[1:]
USER = URL.username
PASSWORD = URL.password
HOST = URL.hostname
PORT = URL.port


db = PostgresqlDatabase(
    DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

# db = PostgresqlDatabase(
#     'local_db',
#     user='germaniakovlev',
#     password='',
#     host='localhost',
#     autorollback=True
# )

class Game(Model):
    '''
    '''
    game_uuid = UUIDField(unique=True)
    word = CharField(max_length=256)
    word_length = IntegerField()
    result = CharField(max_length=16, default='in_progress')
    create_time = DateTimeField(default=datetime.utcnow)
    update_time = DateTimeField(default=datetime.utcnow)
    

    class Meta:
        database = db
    
    def save(self, *args, **kwargs):
        self.update_time = datetime.utcnow()
        return super(Game, self).save(*args, **kwargs)

class LetterGuessed(Model):
    '''
    '''
    game = ForeignKeyField(Game, related_name='letters')
    letter = CharField(max_length=1)
    attempts_left = IntegerField()
    message = CharField(max_length=256)
    create_time = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db
