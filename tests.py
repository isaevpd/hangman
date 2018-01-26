import unittest

from app import app
from models import db, Game, LetterGuessed
import json


class HangmanAPITest(unittest.TestCase):
    def setUp(self):
        """
        Initialize client to send HTTP requests
        and run migrations on the test db
        """
        self.test_client = app.test_client()
        db.connect()
        db.create_tables([Game, LetterGuessed])

    def tearDown(self):
        db.drop_tables([Game, LetterGuessed])

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


if __name__ == '__main__':
    import os
    if os.environ.get('TESTING'):
        unittest.main()
    else:
        raise RuntimeError(
            'Please run "export TESTING=1" before running tests'
        )
