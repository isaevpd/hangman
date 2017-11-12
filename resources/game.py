import uuid
import string

from flask import jsonify, Blueprint, session, abort, make_response
from flask.ext.restful import (
    Resource, Api, reqparse,
    inputs, fields, marshal,
    marshal_with
)

from models import Game, LetterGuessed

from hangman import loadWords, chooseWord


class Representation(fields.Raw):
    def output(self, key, obj):
        return ''.join('_' for _ in obj.word)

class RepresentationLetter(fields.Raw):
    def output(self, key, obj):
        return obj.representation    

class AvailableLetters(fields.Raw):
    def output(self, key, obj):
        return obj.available_letters

class Result(fields.Raw):
    def output(self, key, obj):
        game_new = Game.get(Game.id == obj.game_id)
        return game_new.result


def valid_letter(value):
    user_input = value.lower().strip()
    if not user_input:
        raise ValueError("You didn't provide a letter")
    elif len(user_input) > 1:
        raise ValueError('You provided more than 1 letter')
    elif user_input not in string.ascii_lowercase:
        raise ValueError("You didn't provide a letter from %s" % string.ascii_lowercase)
    return user_input


MAX_ATTEMPTS = 8

# Not using @marshal_with for Word.GET
# GAME_FIELDS = {
#     'word_length': fields.Integer,
#     'game_uuid': fields.String(),
#     'representation': Representation
# }

LETTER_FIELDS = {
    'letter': fields.String(),
    'representation': RepresentationLetter,
    'available_letters': AvailableLetters,
    'attempts_left': fields.Integer(),
    'result': Result,
    'message': fields.String()
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
        Game.create(
            game_uuid=game_uuid,
            word=word,
            word_length=len(word)
        )
 
        output = jsonify(
            word_length=len(word),
            representation= ''.join('_' for _ in word),
            attempts_left=MAX_ATTEMPTS,
            available_letters=string.ascii_lowercase
        )

        resp = make_response(output)
        resp.set_cookie('hangman_game_id', str(game_uuid))
        return resp


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
            'hangman_game_id',
            required=True,
            help='No game_identifier provided',
            location=['cookies']
        )
        super().__init__()

    @marshal_with(LETTER_FIELDS)
    def post(self):
        args = self.reqparse.parse_args()
        # Get game object using uuid from the cookie
        game = Game.get(Game.game_uuid == args['hangman_game_id'])
        letter_guessed = args['letter'].lower()

        def update_game_result(representation):
            if representation == game.word:
                game.result = 'won'

            elif attempts_left == 0:
                game.result = 'lost'

            game.save()

        def create_letter(message):
            return LetterGuessed.create(
                game=game.id,
                letter=letter_guessed,
                #representation=representation,
                attempts_left=attempts_left,
                message=message
            )

        def get_representation(letters_guessed, word):
            return ''.join(map(
                lambda l: l if l in letters_guessed else '_',
                word
            ))
        
        def get_available_letters():
            letters_guessed.add(letter_guessed)
            return ''.join(map(
                lambda l: l if l not in letters_guessed else '',
                string.ascii_lowercase
            ))

        letters = game.letters.select()
        letters_guessed = {l.letter for l in letters}

        try:
            last_letter = letters[-1]
        except IndexError:
            attempts_left = MAX_ATTEMPTS
        else:
            attempts_left = last_letter.attempts_left

        if game.result in ('won', 'lost'):
            return abort(
                400, '{"message": "this game is already over"}'
            )

        elif letter_guessed in letters_guessed:
            message = 'already_guessed'

        elif letter_guessed in game.word:
            letters_guessed.add(letter_guessed)
            message = 'correct_guess'

        else:
            attempts_left = attempts_left - 1
            message = 'incorrect_guess'

        representation = get_representation(letters_guessed, game.word)
        update_game_result(representation)

        letter = create_letter(message)
        letter.available_letters = get_available_letters()
        letter.representation = representation
        return letter


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