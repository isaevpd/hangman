import uuid
import string

from flask import jsonify, Blueprint, session
from flask.ext.restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with)

from models_1 import Game, LetterGuessed

from hangman import loadWords, chooseWord, getGuessedWord


class Representation(fields.Raw):
    def output(self, key, obj):
        #
        return ''.join('_' for _ in obj.word)


class Result(fields.Raw):
    def output(self, key, obj):
        game_new = Game.get(Game.id == obj.game_id)
        return game_new.result


def valid_letter(value):
    if value.lower() not in string.ascii_letters:
        raise ValueError(
            "You didn't provide a letter from 'abcdefghijklmnopqrstuvwxyz'")
    return value


MAX_ATTEMPTS = 8

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

        def update_game_result(updated_representation):
            if updated_representation == game.word:
                game.result = 'won'
                game.save()

            elif attempts_left == 0:
                game.result = 'lost'
                game.save()

        def already_guessed():
            letter = LetterGuessed.create(
                game=game.id,
                letter=letter_guessed,
                representation=representation,
                letters_guessed=track_letters_guessed(letters_guessed),
                attempts_left=attempts_left,
                message='already_guessed')
            print('result update status ----- already guessed' +
                  str(game.word == representation))
            return letter

        def incorrect_guess():
            '''
            '''
            letter = LetterGuessed.create(
                game=game.id,
                letter=letter_guessed,
                representation=representation,
                letters_guessed=track_letters_guessed(letters_guessed),
                attempts_left=attempts_left,
                message='incorrect_guess')

            update_game_result(representation)
            return letter

        def correct_guess():
            '''
            '''
            letter_indices = [index for index, letter in enumerate(
                game.word) if letter == letter_guessed]
            updated_representation = ''.join(
                letter_guessed if index in letter_indices
                else letter for index, letter in enumerate(representation))

            letter = LetterGuessed.create_letter(
                game=game.id,
                letter=letter_guessed,
                representation=updated_representation,
                letters_guessed=track_letters_guessed(letters_guessed),
                attempts_left=attempts_left,
                message='correct_guess')

            update_game_result(updated_representation)
            return letter

        def track_letters_guessed(letters_guessed):
            if letter_guessed not in letters_guessed:
                letters_guessed += letter_guessed
            return letters_guessed

        try:
            letter = game.letters.get()

        except LetterGuessed.DoesNotExist:
            attempts_left = MAX_ATTEMPTS  # 8
            representation = '_' * len(game.word)
            letters_guessed = ''

        else:
            attempts_left = letter.attempts_left
            representation = letter.representation
            letters_guessed = letter.letters_guessed

        if game.result in ('won', 'lost'):
            return game.letters.get()

        elif letter_guessed in letters_guessed:
            return already_guessed()

        elif letter_guessed in game.word:
            return correct_guess()

        else:
            attempts_left = attempts_left - 1
            return incorrect_guess()


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
