import os
import random
import smtplib
import ssl
import string

import MySQLdb.cursors
import bcrypt
from captcha.image import ImageCaptcha
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import requests
import json

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'project'

# Intialize MySQL
mysql = MySQL(app)


# http://localhost:5000/project/ - this will be the login page, we need to use both GET and POST #requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:  # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Extract the Symmetric-key from Accounts DB
            key = account['symmetrickey']
            # Load the key
            f = Fernet(key)
            # Call f.decrypt() to decrypt the data. Convert data from Database to bytes/binary by using.encode()
            decryptedEmail_Binary = f.decrypt(account['email'].encode())
            # call .decode () to convert from Binary to String – to be displayed in Home.html.
            decryptedEmail = decryptedEmail_Binary.decode()
            # Extract the Salted-hash password from DB to local variable
            hashAndSalt = account['password']

            # Convert salted-hash password to bytes by using the .encode() method
            # bycrypt.checkpw () will verify if the password input by user matches that from the database
            if bcrypt.checkpw(password.encode(), hashAndSalt.encode()):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['email'] = decryptedEmail

                session['2fa'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                port = 587
                smtp_server = "smtp.gmail.com"
                sender_email = "secproj123test@gmail.com"
                receiver_email = session['email']
                password = 'Project123'
                message = """\
                    Subject: 2FA

                    Code: {}.""".format(session['2fa'])

                context = ssl.create_default_context()
                with smtplib.SMTP(smtp_server, port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)

                return redirect(url_for('submitcode'))
        else:
            # Account doesn’t exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')


@app.route('/project/submitcode', methods=['GET', 'POST'])
def submitcode():
    if request.method == 'POST':
        inputcode = request.form['code']
        if inputcode.upper() == session['2fa']:
            login = datetime.now().strftime("%X %x")
            session['login'] = login

            # Your API key, available from your account page
            YOUR_GEOLOCATION_KEY = '3b1399cd7b1947a0a2b8fd3a3f92e285'

            # URL to send the request to
            request_url = 'https://ipgeolocation.abstractapi.com/v1/?api_key=' + YOUR_GEOLOCATION_KEY
            # Send request and decode the result
            response = requests.get(request_url)
            result = json.loads(response.content)

            info = {
                'city': result['city'],
                'country': result['country'],
                'continent': result['continent'],
                'is_vpn': result['security']['is_vpn']
                }

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO AuditInfo VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)',
                           (session['username'], login, 'did not logout', info['city'], info['country'], info['continent'], info['is_vpn']))
            mysql.connection.commit()

            return redirect(url_for('home'))

    return render_template('submitcode.html', msg='')


# http://localhost:5000/project/logout - this will be the logout page
@app.route('/project/logout')
def logout():
    logout = datetime.now().strftime("%X %x")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE AuditInfo SET logout = %s WHERE login = %s', (logout, session['login']))
    mysql.connection.commit()
    # Remove session data, this will log the user out session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)  # Redirect to login page
    return redirect(url_for('login'))


@app.route('/project/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    image = ImageCaptcha(width=280, height=90)
    data = image.generate('hello17world')
    image.write('hello17world', 'demo.png')
    os.replace('demo.png', 'static/demo.png')

    # Check if "username", "password" and "email" POST requests exist (user submitted form)

    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'gender' in request.form and 'address' in request.form:
        # Create variables for easy access
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        gender = request.form['gender']
        address = request.form['address']

        # Password Hashing
        # Create a random number (Salt)
        salt = bcrypt.gensalt(rounds=16)
        # A hashed value is created with hashpw() function, which takes the cleartext value and a salt as parameters.
        hash_password = bcrypt.hashpw(password.encode(), salt)

        # Symmetric Key Encryption
        # Generate a random Symmetric key. Keep this key in your database
        key = Fernet.generate_key()

        # Load the key into the Crypto API
        f = Fernet(key)

        # Encrypt the email and convert to bytes by calling f.encrypt()
        encryptedEmail = f.encrypt(email.encode())

        # Insert Salted-hash password get inserted into the Accounts table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (username, firstname, lastname, hash_password, encryptedEmail, gender, address, key))
        mysql.connection.commit()
        msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/project/home - this will be the home page, only accessible for loggedin users
@app.route('/project/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])  # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/project/profile - this will be the profile page, only accessible for loggedin users
@app.route('/project/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info

        return render_template('profile.html', account=account)  # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/project/change_password
@app.route('/project/change_password', methods=['GET', 'POST'])
def change_password():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'new password' in request.form:
        if session['email'] == request.form['email']:
            # Create variables for easy access
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
            # Fetch one record and return result
            account = cursor.fetchone()

            email = request.form['email']
            new_password = request.form['new password']
            salt = bcrypt.gensalt(rounds=16)
            hash_password = bcrypt.hashpw(new_password.encode(), salt)
            if 'loggedin' in session:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE accounts SET password = %s WHERE email = %s', (hash_password, account['email']))
                mysql.connection.commit()
                msg = 'Password successfully changed!'
                return render_template('home.html', msg=msg)
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    return render_template('change_password.html', msg=msg)


# http://localhost:5000/project/login_activity_list
@app.route('/project/login_activity_list')
def login_activity_list():
    msg = ''
    list_info = []
    print(session['username'])
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM auditinfo WHERE username = %s', (session['username'],))
    auditinfo = cursor.fetchall()
    for i in auditinfo:
        list_info.append((i['login'], i['logout'], i['city'], i['country'], i['continent'], i['is_vpn']))
    print(list_info)
    return render_template('login_activity_list.html', msg=msg, info=list_info)


# http://localhost:5000/project/forget_password
@app.route('/project/forget_password', methods=['GET', 'POST'])
def forget_password():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'username' in request.form:
        session['email'] = request.form['email']
        session['username'] = request.form['username']
        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = "secproj123test@gmail.com"
        receiver_email = session['email']
        password = 'Project123'
        message = """\
            Subject: forget password

            Link: {}.""".format('http://127.0.0.1:5000/project/change')

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        return render_template('submiturl.html')
    return render_template('forget_password.html', msg=msg)


# http://localhost:5000/project/submiturl
@app.route('/project/submiturl')
def submiturl():
    return render_template('submiturl.html')


# http://localhost:5000/project/change
@app.route('/project/change', methods=['GET', 'POST'])
def change():
    msg = ''
    if request.method == 'POST' and 'new password' in request.form:
        # Create variables for easy access
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
        # Fetch one record and return result
        account = cursor.fetchone()

        new_password = request.form['new password']
        salt = bcrypt.gensalt(rounds=16)
        hash_password = bcrypt.hashpw(new_password.encode(), salt)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE accounts SET password = %s WHERE email = %s', (hash_password, account['email']))
        mysql.connection.commit()
        msg = 'Password successfully changed!'
        return render_template('index.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    return render_template('change.html', msg=msg)


if __name__ == '__main__':
    app.run()
