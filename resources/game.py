from flask import jsonify, Blueprint, session
from flask.ext.restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with)

from models_1 import Game, LetterGuessed
import random
import time
from hangman import loadWords, chooseWord, getGuessedWord

GAME_FIELDS = {
    'game_id': fields.Float,
    'word_length': fields.Integer,
    'word': fields.String(),
}


class Word(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'word',
            required=True,
            help='No word provided!',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        word = chooseWord(loadWords())
        user_identifier = time.time()
        repres = ''
        for i in word:
            repres += '_'
        models_1.Game.create_game(user_identifier, word, len(word))
        return jsonify(word_length=len(word), word=word, visual=repres, user_identifier=user_identifier)

    def post(self):
        print(session['id'])
        return session['id']


class Letter(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'letter',
            required=True,
            help='Letter not provided',
            location=['form', 'json']
        )

        self.reqparse.add_argument(
            'user_identifier',
            required=True,
            help='No user_identifier provided',
            location=['form','json']
        )
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        game_id = Game.get(Game.user_identifier==args['user_identifier']).id
        word = Game.get(Game.user_identifier==args['user_identifier']).word
        print(game_id)
        letters_used = ''
        game_letters = LetterGuessed.select().where(LetterGuessed.game_id_id == game_id)
        for i in game_letters:
            letters_used += i.letter
        print(letters_used)
        guessed_word = getGuessedWord(word,letters_used)
        print(guessed_word)
        


        


game_api = Blueprint('resources.game', __name__)
api = Api(game_api)
api.add_resource(
    Word,
    '/api/v1/word',
    endpoint=''
)

api.add_resource(
    Letter,
    '/api/v1/letter'
)
