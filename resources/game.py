import uuid, string

from flask import jsonify, Blueprint, session
from flask.ext.restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with)

from models_1 import Game, LetterGuessed

from hangman import loadWords, chooseWord, getGuessedWord


class Representation(fields.Raw):
    def output(self, key, obj):
        return ''.join('_' for _ in obj.word)

class Result(fields.Raw):
    def output(self, key, obj):
        if obj.attempts_left == 0:
            return 'lost'
        elif '_' not in obj.representation:
            return 'won'
        else:
            return 'in_progress'

def valid_letter(value):
    if value.lower() not in string.ascii_letters:
        raise ValueError("You didn't provide a letter from 'abcdefghijklmnopqrstuvwxyz'")
    return value


GAME_FIELDS = {
    'word_length': fields.Integer,
    'game_uuid': fields.String(),
    'representation': Representation
}

LETTER_FIELDS = {
    'letter': fields.String(),
    'representation': fields.String(),
    'attempts_left': fields.Integer(),
    'result': Result,
    'message': fields.String()
}


class Word(Resource):
    '''
    Used once per game when the game is initialized.
    '''
    @marshal_with(GAME_FIELDS)
    def get(self):
        '''
        Generates random word, game UUID and creates a DB entry for a new game.
        '''
        word = chooseWord(loadWords())
        game_uuid = uuid.uuid4()
        representation = ''
        for letter in word:
            representation += '_'
        Game.create_game(game_uuid, word, len(word))
        return Game.get(Game.game_uuid == game_uuid)


class Letter(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'letter',
            required=True,
            type=valid_letter,
            #help='Letter not provided',
            location=['form', 'json']
        )

        self.reqparse.add_argument(
            'game_uuid',
            required=True,
            help='No game_identifier provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(LETTER_FIELDS)
    def post(self):
        args = self.reqparse.parse_args()
        # Get game object using uuid from the cookie
        game = Game.get(Game.game_uuid == args['game_uuid'])
        letter_guessed = args['letter'].lower()

        try:
            letter = game.letters.get()
            if (letter.attempts_left > 0 and letter_guessed not in letter.representation
                    and letter_guessed in game.word):

                # code for successfull guess
                letter_indices = [index for index, letter in enumerate(
                    game.word) if letter == letter_guessed]
                representation = ''.join(
                    letter_guessed if index in letter_indices
                    else letter for index, letter in enumerate(letter.representation))

                LetterGuessed.create_letter(
                    game.id,
                    letter_guessed,
                    representation,
                    letter.attempts_left,
                    'good_guess')

                return game.letters.get()

            elif (letter.attempts_left > 0
                  and args['letter'] not in letter.representation
                  and args['letter'] not in game.word):

                # code for failed guess
                LetterGuessed.create_letter(
                    game.id,
                    letter_guessed,
                    letter.representation,
                    letter.attempts_left - 1,
                    'bad_guess')

                return game.letters.get()

            elif (letter.attempts_left > 0
                  and args['letter'] in letter.representation):

                # code for exisiting letter guessed
                LetterGuessed.create_letter(
                    game.id,
                    letter_guessed,
                    letter.representation,
                    letter.attempts_left,
                    'already_exists')

                return game.letters.get()

        except LetterGuessed.DoesNotExist:
            if letter_guessed in game.word:
                representation = (''.join(i if i == letter_guessed
                                           else '_' for i in game.word))

                LetterGuessed.create_letter(
                    game.id,
                    letter_guessed,
                    representation,
                    8,
                    'good_guess')
            
                return game.letters.get()
            else:
                LetterGuessed.create_letter(
                    game.id,
                    letter_guessed,
                    ''.join('_' for _ in game.word),
                    7,
                    'bad_guess')
                
                return game.letters.get()

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
