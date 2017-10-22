import uuid

from flask import jsonify, Blueprint, session
from flask.ext.restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with)

from models_1 import Game, LetterGuessed

from hangman import loadWords, chooseWord, getGuessedWord

GAME_FIELDS = {
    'game_id': fields.Float,
    'word_length': fields.Integer,
    'word': fields.String(),
}


class Word(Resource):
    '''
    Used once per game when the game is initialized.
    '''
    def get(self):
        '''
        Generates random word, game UUID and creates a DB entry for a new game.
        '''
        word = chooseWord(loadWords())
        game_uuid = uuid.uuid4()
        presentation = ''
        for letter in word:
            presentation += '_'
        Game.create_game(game_uuid, word, len(word))
        return jsonify(word_length=len(word), presentation=presentation, game_uuid=game_uuid)


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
            location=['form', 'json']
        )
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        game_id = Game.get(Game.user_identifier == args['user_identifier']).id
        word = Game.get(Game.user_identifier == args['user_identifier']).word
        print(game_id)
        letters_used = ''
        game_letters = LetterGuessed.select().where(LetterGuessed.game_id == game_id)
        for i in game_letters:
            letters_used += i.letter
        print(letters_used)
        guessed_word = getGuessedWord(word, letters_used)
        print(guessed_word)

game_api = Blueprint('resources.game', __name__)
api = Api(game_api)
api.add_resource(
    Word,
    '/api/v1/word'
)

api.add_resource(
    Letter,
    '/api/v1/letter'
)
