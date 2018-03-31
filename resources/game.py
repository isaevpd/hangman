import string
import uuid

from flask import (
    jsonify,
    Blueprint,
    abort,
    make_response,
    redirect,
    url_for,
    render_template
)
from flask_restful import (
    Resource, Api, reqparse
)

from constants import MAX_ATTEMPTS, STATUS_IN_PROGRESS
from models import Game, LetterGuessed, CustomWord
from utils import choose_word


def valid_letter(value):
    user_input = value.lower().strip()
    if not user_input:
        raise ValueError("You didn't provide a letter")
    elif len(user_input) > 1:
        raise ValueError('You provided more than 1 letter')
    elif user_input not in string.ascii_lowercase:
        raise ValueError(
            f"You didn't provide a letter from {string.ascii_lowercase}"
        )
    return user_input


class Word(Resource):
    """
    Used once per game when the game is initialized.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'custom_word_id',
            required=False,
            type=uuid.UUID,
            help='No game_identifier provided',
            location=['cookies']
        )
        super().__init__()

    def post(self):
        """
        Generates random word, game UUID and creates a DB entry for a new game.
        """
        args = self.reqparse.parse_args()
        try:
            word = CustomWord.objects.get(
                uuid=args.get('custom_word_id')
            ).word
        except (ValueError, CustomWord.DoesNotExist):
            word = choose_word()

        game = Game.objects.create(
            word=word
        )

        output = jsonify(
            word_length=len(word),
            representation='_' * len(word),
            attempts_left=MAX_ATTEMPTS,
            available_letters=string.ascii_lowercase
        )

        resp = make_response(output)
        # Cookie expires in 24 hours
        resp.set_cookie('hangman_game_id', str(game.uuid), 86400)
        return resp


class Letter(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'letter',
            required=False,
            type=valid_letter,
            help='Letter not provided',
            location=['form', 'json']
        )

        self.reqparse.add_argument(
            'hangman_game_id',
            required=True,
            type=uuid.UUID,
            help='No game_identifier provided',
            location=['cookies']
        )
        super().__init__()

    def get(self):
        args = self.reqparse.parse_args()
        try:
            game = Game.objects.get(uuid=args['hangman_game_id'])
        except (Game.DoesNotExist, ValueError):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('hangman_game_id', '', expires=0)
            return resp

        word = game.word
        word_length = game.word_length
        if not game.letters:
            return jsonify(
                word_length=word_length,
                representation=''.join('_' for _ in word),
                attempts_left=MAX_ATTEMPTS,
                available_letters=string.ascii_lowercase
            )
        else:
            letters_guessed = game.letters_guessed
            last_letter = game.last_letter

            representation = game.representation
            available_letters = game.get_available_letters(letters_guessed)

            return jsonify(
                word_length=word_length,
                representation=representation,
                attempts_left=last_letter.attempts_left,
                available_letters=available_letters
            )

    def post(self):
        args = self.reqparse.parse_args()
        try:
            game = Game.objects.get(uuid=args['hangman_game_id'])
        except (Game.DoesNotExist, ValueError):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('hangman_game_id', '', expires=0)
            return resp

        word = game.word
        letter = args['letter']
        letters_guessed = game.letters_guessed

        try:
            last_letter = game.last_letter
        except IndexError:
            attempts_left = MAX_ATTEMPTS
        else:
            attempts_left = last_letter.attempts_left

        if game.is_over:
            return abort(
                400, '{"message": "this game is already over"}'
            )

        elif letter in letters_guessed:
            message = 'already_guessed'

        elif letter in word:
            letters_guessed.add(letter)
            message = 'correct_guess'

        else:
            attempts_left = attempts_left - 1
            message = 'incorrect_guess'

        letter = game.append_letter(letter, attempts_left, message)

        letter.available_letters = game.get_available_letters(
            letters_guessed | {letter.letter}
        )

        # send back the original word if game is over
        if game.is_over:
            original_word = game.word
        else:
            original_word = None

        return jsonify(
            word_length=len(word),
            letter=letter.letter,
            representation=game.representation,
            available_letters=letter.available_letters,
            attempts_left=attempts_left,
            status=game.status,
            message=message,
            original_word=original_word
        )


class GameLink(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'word',
            required=True,
            type=str,
            help='Letter not provided',
            location=['form', 'json']
        )
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        word = args['word']
        try:
            word_uuid = CustomWord.objects.get(
                word=word
            ).uuid
        except CustomWord.DoesNotExist:
            word_uuid = CustomWord.objects.create(
                word=word
            ).uuid
        return jsonify(
            word_uuid=word_uuid
        )


class GameLinkActivation(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser(bundle_errors=True)
        self.reqparse.add_argument(
            'hangman_game_id',
            required=False,
            type=uuid.UUID,
            location=['cookies']
        )
        super().__init__()

    def get(self, word_uuid):
        resp = make_response(render_template('hangman.html'))
        resp.set_cookie('custom_word_id', str(word_uuid), 86400)
        # if cookie doesn't match the game - reset it
        game_cookie = self.reqparse.parse_args().get('hangman_game_id')
        current_game = Game.objects.filter(uuid=game_cookie).first()
        if current_game is None:
            return resp
        try:
            word = CustomWord.objects.get(uuid=word_uuid).word
        except (CustomWord.DoesNotExist, ValueError):
            word = None

        if current_game.word != word or current_game.status != STATUS_IN_PROGRESS:
            resp.set_cookie('hangman_game_id', '', expires=0)
        return resp


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

api.add_resource(
    GameLink,
    '/api/v1/game_link'
)

api.add_resource(
    GameLinkActivation,
    '/activate/<string:word_uuid>'
)
