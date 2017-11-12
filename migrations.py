import urllib.parse as urlparse
import os
import psycopg2
from peewee import *
from playhouse.migrate import *

from models import Game, LetterGuessed

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
#     host='localhost'
# )

db.connect()
db.create_tables([Game, LetterGuessed])
