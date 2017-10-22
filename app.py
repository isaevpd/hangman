from flask import Flask, flash, render_template, request, redirect, url_for, make_response, session
import json, ast
from hangman import *
from models_1 import (
    db,
    create_result,
    create_word,
    user,
    word_created
)

from resources.game import game_api

app = Flask(__name__)
app.secret_key = 'some_secret'
app.register_blueprint(game_api)

# Gets user game data saved in the cookie
def get_saved_data():
    '''
    Get and parse cookie data
    '''
    try:
        data = request.cookies.get('game_data')
        data = ast.literal_eval(data)
    except ValueError:
        data = {}
    return data

def set_secret_word(data):
    '''
    '''
    if data == {}:
        secretWord = chooseWord(wordlist).lower()
        data = {
            'word': secretWord,
            'attempts': 8,
            'user_letters': '',
            'return_msg': 'Let\'s start playing'
            }
    return data

def get_user_letter():
    '''
    Input: webform string
    Output: lowercase string
    '''
    user_letter = request.form['user_letter_field'].lower()
    return user_letter
    
@app.route('/', methods=['GET', 'POST'])
def index():
    data = get_saved_data()
    data = set_secret_word(data)
    print('user_data: ' + str(data))

    available_letters = getAvailableLetters(data['user_letters'])
    guessed_word = getGuessedWord(data['word'], data['user_letters'])
    word = data['word']
    attempts = data['attempts']
    result = isWordGuessed(data['word'],data['user_letters'])
    print('available_letters: ' + available_letters)
    print('guessed_word: ' + guessed_word)
    print('user_letters: ' + data['user_letters'])
    print(data)

    if result or attempts == 0:
        db.get_conn()
        create_result(word, attempts, result)
        if result:
            flash('Congrats! You\' won the game!')
        else:
            flash('Try next time!')
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('game_data', '', expires=0)
        return resp 

    output = {
        'word_length': len(data['word']),
        'available_letters': available_letters,
        'guessed_word': guessed_word,
        'attempts': data['attempts'],
        'message': data['return_msg']
    }

    resp = make_response(render_template('index.html', **output))
    resp.set_cookie('game_data', str(data))
    return resp


@app.route('/get_data', methods=['POST'])
def get_data():
    user_letter = get_user_letter()
    print('___________user letter_________ ' + user_letter)
    data = get_saved_data()
    import string

    if user_letter in data['user_letters'] and user_letter != '':
        flash('Ooops! You have already tried this letter. Try something new!')
    elif user_letter not in string.ascii_lowercase or user_letter == '':
        flash('You forgot to enter the letter!')
    elif user_letter in data['word']:
        data['user_letters'] += user_letter
        flash('Great guess!')
    elif user_letter not in data['word']:
        data['user_letters'] += user_letter
        data['attempts'] -= 1
        flash('Boom, this letter is not in the secret word!')

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('game_data', str(data))
    return resp

@app.route('/reset_cookie', methods=['GET','POST'])
def reset_cookie():
    '''
    Reset client-side game data
    '''
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('game_data', '', expires=0)
    return resp

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    User registration view.
    '''
    logged_in = None

    if request.method == 'GET':
        if 'nickname' in session:
            logged_in = True
            output = {
                'login_state': 'You have already registered with nickname: %s' % session['nickname']
            }
            print('User logged in: ' + str(logged_in))
            return render_template('register.html', **output, logged_in=logged_in)
        logged_in = False
        return render_template('register.html', logged_in=logged_in)
    else:
        session['nickname'] = request.form['nickname']
        # Create user in user table
        if user.select().where(user.nickname == session['nickname']).exists():
            print('User %s already exists!' % session['nickname'])
            return redirect(url_for('register'))
        user.create_user(session['nickname'])
        return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'nickname' in session:
            return redirect(url_for('add_word'))
        return render_template('login.html')
    else:
        nickname = request.form['nickname']
        try:
            nickname_check = user.get(user.nickname == nickname)
            print('user in db %s' % nickname_check.nickname)
            if nickname == nickname_check.nickname:
                session['nickname'] = nickname
                return 'You are logged in'
        except user.DoesNotExist:
            return 'No user with this nickname'


@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    '''
    View to add user words for multiplayer.
    '''
    if request.method == 'GET':
        if 'nickname' in session:
            return render_template('add_word.html', logged_in=True)
        return render_template('add_word.html', logged_in=False)
    else:
        session['word']=request.form['word'].lower() 
        db.get_conn()
        user_id = user.select(user.id).where(user.nickname == session['nickname'])
        create_word(session['word'], user_id)
        # Remove created word from session if it's there
        session.pop('word', None)
        flash('Success! We\'ve saved your word!')
        return redirect(url_for('add_word'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')



if __name__ == '__main__':
     app.debug = True
     port = int(os.environ.get("PORT", 5000))
     app.run(host='0.0.0.0', port=port)