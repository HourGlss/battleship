from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template("templates/index.html")


@main.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('templates/register.html')


@main.route('/game')
def game():
    return