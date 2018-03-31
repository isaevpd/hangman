import json
import unittest

from mongoengine import connection

from app import app
from models import Game


class HangmanAPITest(unittest.TestCase):
    def setUp(self):
        """
        Initialize client to send HTTP requests
        and run migrations on the test db
        """
        self.test_client = app.test_client()
        connection.disconnect()
        connection.connect('hangman_test')

    def tearDown(self):
        connection.get_connection().drop_database('hangman_test')
        connection.get_connection().close()

    def test_post_word(self):
        """
        POST to /api/v1/word/' results in
        game entry created in the database
        and JSON response of the form:
        {
            word_length: int,
            representation: '_' * word_length,
            attempts_left: some constant,
            available_letters: all lowercase ascii letters
        }
        """
        game_count = Game.objects.count()
        response = self.test_client.post('/api/v1/word')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        expected_fields = {
            'word_length',
            'representation',
            'attempts_left',
            'available_letters'
        }
        self.assertEqual(
            set(data),
            expected_fields
        )
        self.assertEqual(Game.objects.count(), game_count + 1)

    def test_get_letter(self):
        # create a game and save cookie
        self.test_client.post('/api/v1/word')
        response = self.test_client.get('/api/v1/letter')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        expected_fields = {
            'word_length',
            'representation',
            'attempts_left',
            'available_letters'
        }
        self.assertEqual(
            set(data),
            expected_fields
        )

    def test_post_first_letter(self):
        # create a game and save cookie
        self.test_client.post('/api/v1/word')
        response = self.test_client.post(
            '/api/v1/letter',
            data=json.dumps({'letter': 'a'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        game = Game.objects.first()

        expected_data = {
            'word_length': game.word_length,
            'letter': 'a',
            'representation': game.representation,
            'available_letters': game.get_available_letters(),
            'attempts_left': game.last_letter.attempts_left,
            'status': game.status,
            'message': game.last_letter.message,
            'original_word': None
        }
        self.assertDictEqual(data, expected_data)
