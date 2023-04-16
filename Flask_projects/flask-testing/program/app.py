import os
from flask import Flask, request, render_template, flash, url_for, redirect
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '8daa7770bbfb5d1225fc19d5817c492e'


PASSWORD_HASH = os.environ.get('PASSWORD_HASH')

if not PASSWORD_HASH:
    PASSWORD = 'mysecurepassword'
    PASSWORD_HASH = generate_password_hash(PASSWORD, method='pbkdf2:sha256', salt_length=16)
    os.environ['PASSWORD_HASH'] = PASSWORD_HASH

@app.route('/')
def check():
    password = request.args.get('password')
    if password is None:
        return render_template('password.html')
    
    if check_password_hash(PASSWORD_HASH, password):
        flash('Correct Password!', 'success')
    else:
        flash('Incorrect Password!', 'danger')
    
    return render_template('password.html')

if __name__ == '__main__':
    app.run()
