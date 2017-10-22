import urllib.parse as urlparse
import os
import psycopg2
from peewee import *

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

class Result(Model):
    '''
    Creates Result table
    '''
    word = CharField(max_length=256)
    attempts = IntegerField()
    result = BooleanField()

    class Meta:
        database = db

# Utility function
def initialize():
    db.connect()
    db.create_tables([Result], safe=True)

def create_result(word, attempts, result):
    '''
    Creates an entry with the game result
    '''
    Result.create(word=word, attempts=attempts, result=result)
