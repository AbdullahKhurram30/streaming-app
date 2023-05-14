from flask import render_template, request, redirect, url_for
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, ValidationError
import json
import requests

try:
    from app import app, db, login_manager, bcrypt
except ImportError:
    from __init__ import app, db, login_manager, bcrypt

@app.before_first_request
def create_tables():
    '''
    This function is used to create the tables in the database
    '''
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    '''
    This function is used to load the user from the database
    '''
    return User.query.get(int(user_id))

# make a class for users
class User(db.Model, UserMixin):
    '''
    This class is used to create the user objects

    Attributes:
        id: the id of the user
        username: the username of the user
        password: the password of the user

    Methods:
        __repr__: returns the string representation of the object
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')" # this is the string representation of the object
    
# make a class for the registration form
class RegistrationForm(FlaskForm):
    '''
    This class is used to create the registration form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button

    Methods:
        validate_username: validates the username
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        '''
        This function is used to validate the username
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
# make a class for the login form
class LoginForm(FlaskForm):
    '''
    This class is used to create the login form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    '''
    This function is used to render the home page which is the same as the login page
    '''
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This function is used to render the login page
    '''
    # create the login form
    form = LoginForm()
    # check if the form is valid
    if form.validate_on_submit():
        # get the user from the database
        user = User.query.filter_by(username=form.username.data).first()
        # check if the user exists
        if user:
            # check if the password is correct
            if bcrypt.check_password_hash(user.password, form.password.data):
                # login the user
                login_user(user)
                # redirect to the dashboard
                return redirect(url_for('dashboard'))
        # if the user does not exist or the password is incorrect
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', form=form, error=error)
    # if the form is not valid
    else:
        return render_template('login.html', form=form)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    This function is used to render the registration page
    '''
    # create the registration form
    form = RegistrationForm()
    # check if the form is valid
    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create the user object
        user = User(username=form.username.data, password=hashed_password)
        # add the user to the database
        db.session.add(user)
        db.session.commit()
        # redirect to the login page
        return redirect(url_for('dashboard'))
    else:
        error = 'Username already exists.'
        return render_template('register.html', form=form, error=error)
    
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    '''
    This function is used to logout the user
    '''
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

#device_url = ## add url

@app.route('/stream')
@login_required
def stream():
    return render_template('streaming.html')

# def send_command():
#     # get the command from the form data
#     command = request.form['command']

#     # create a payload for the command
#     payload = {
#         'command': command
#     }

#     # send the command to the device
#     response = requests.post(device_url, json=payload)

#     # get the response from the device
#     response = response.json()

#     # display the response on the web application
#     return render_template('streaming.html', response=response)