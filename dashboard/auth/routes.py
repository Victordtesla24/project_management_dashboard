from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from dashboard.auth.middleware import authenticate, create_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate(username, password):
            # Create JWT token and set in cookie
            token = create_token({'username': username})
            session['user'] = username
            response = redirect(request.args.get('next') if request.args.get('next') else url_for('dashboard.index'))
            response.set_cookie('auth_token', token)
            return response
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
