from flask import Flask, flash, render_template, request, redirect, url_for, make_response, session

from resources.game import game_api

app = Flask(__name__)
app.register_blueprint(game_api)
    
@app.route('/hangman')
def hangman():
    return render_template('hangman.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game_over')
def game_over():
    return render_template('game_over.html')

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'

if __name__ == '__main__':
    app.debug = True
