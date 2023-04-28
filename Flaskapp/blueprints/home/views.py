from flask import Blueprint, render_template

bp = Blueprint('home' , __name__ )

# Home page of app
@bp.route('/')
def index():
    try:
        return render_template('home/home.html')
    except Exception as e:
        return render_template('error/error-404.html' , error=e)