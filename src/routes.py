from flask import Blueprint

main = Blueprint('main', __name__)


@main.route('/game')
def game():
    return
