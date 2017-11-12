from flask import Flask, flash, render_template, request, redirect, url_for, make_response, session

from resources.game import game_api

app = Flask(__name__)
app.secret_key = 'some_secret'
app.register_blueprint(game_api)
    
@app.route('/', methods=['GET'])
def index():
    return 'Home page should be here'

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'

if __name__ == '__main__':
     app.debug = True
     port = int(os.environ.get("PORT", 5000))
     app.run(host='0.0.0.0', port=port)
