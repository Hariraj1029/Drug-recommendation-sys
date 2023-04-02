import pandas as pd
from flask import Flask, session, render_template, request, redirect, url_for
from jinja2 import Environment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd


app = Flask(__name__, static_folder='static')
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1029@localhost:3306/drug-recommendation'
db = SQLAlchemy(app)

engine = create_engine(
    'mysql://root:root1029@localhost:3306/drug-recommendation')
Session = sessionmaker(bind=engine)
ses = Session()


class Review(db.Model):
    revId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drugName = db.Column(db.String(80),
                         nullable=False)
    condition = db.Column(db.String(120), nullable=False)
    commentsReview = db.Column(db.String(500), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    sideEffects = db.Column(db.String(80), unique=False, nullable=False)
    sideEffectsReview = db.Column(db.String(500), unique=False, nullable=False)
    effectiveness = db.Column(db.Integer, unique=False, nullable=False)
    benefitsReview = db.Column(db.String(500), unique=False, nullable=False)
    sideEffectsKeywords = db.Column(
        db.String(500), unique=False, nullable=False)


class User(db.Model):
    email = db.Column(db.String(80), unique=True,
                      nullable=False, primary_key=True)
    password = db.Column(db.String(120), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)

env = Environment()
env.globals['int'] = int

# Read the CSV file data
df = pd.read_csv('total.csv')

@app.route('/')
def home():
    return render_template('index.html')
    

@app.route('/upload')
def upload():

    # Iterate the CSV file and insert data into MySQL database
    for index, row in df.iterrows():
        record = Review(drugName=str(row['urlDrugName']),
                        condition=str(row['condition']),
                        commentsReview=str(row['commentsReview']),
                        rating=row['rating'],
                        sideEffects=row['sideEffects'],
                        sideEffectsReview=row['sideEffectsReview'],
                        effectiveness=row['effectiveness'],
                        benefitsReview=row['benefitsReview'],
                        sideEffectsKeywords=row['se_keywords'])
        db.session.add(record)
    db.session.commit()

    return 'File uploaded successfully'


@app.route('/rev-added', methods=['POST', 'GET'])
def rev_added():
    if (request.method == 'POST'):
        drugName = request.form.get('drugname')
        condition = request.form.get('condition')
        commentsReview = request.form.get('comment')
        rating = request.form.get('rating')
        sideEffects = request.form.get('sideEffects')
        sideEffectsReview = request.form.get('sideeff')
        effectiveness = request.form.get('effectiveness')
        benefitsReview = request.form.get('benefitsReview')
        sideEffectsKeywords = request.form.get('se-key')
        entry = Review(drugName=drugName,
                       condition=condition,
                       commentsReview=commentsReview,
                       rating=rating,
                       sideEffects=sideEffects,
                       sideEffectsReview=sideEffectsReview,
                       effectiveness=effectiveness,
                       benefitsReview=benefitsReview,
                       sideEffectsKeywords=sideEffectsKeywords)
        db.session.add(entry)
        db.session.commit()
    return render_template('index.html')


@app.route('/user-register', methods=['POST', 'GET'])
def user_register():
    return render_template('register.html')


@app.route('/user-login', methods=['POST', 'GET'])
def user_login():
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        email_id = request.form.get('email_id')
        log = User.query.filter_by(email=email_id).first()
        if log is not None:
            session['username'] = log.username
            print('already exists')
            return render_template('home.html', username=session['username'])
        else:
            entry = User(username=username,
                         password=password, email=email_id)
            db.session.add(entry)
            db.session.commit()
    return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])  # route for login page
def login():
    if request.method == 'POST':  # if method is post
        email_id = str(request.form.get('email_id'))  # getting email from form
        userpass = str(request.form.get('password'))  # getting password from form
        # getting entry from database with email and password
        log = User.query.filter_by(email=email_id, password=userpass).first()
        print(log.username)
        if log is not None:  # if entry exists
            session['email'] = email_id  # setting session for email
            session['username'] = log.username  # setting session for username
            msg = 'Logged in successfully !!'  # setting message
            render_template('login.html', msg=msg)
            # rendering home page
            return render_template('index.html', username=session['username'])
        else:
            msg = 'Incorrect email / password !!'
            return render_template('login.html', msg=msg)

    return render_template('login.html')


@app.route('/addrev')
def addrev():
    return render_template('addrev.html')


# API endpoint to send the data
@app.route('/searched', methods=['POST'])
def getDrugs():
    # print(data)
    # Do something with the data
    user_condition = request.form.get('search')

    # Getting the rows which are having rating > 5 and also satisfied the user condition
    gt5 = test_data[test_data['rating'] > 5]
    cond_rows = gt5[gt5['condition'] == user_condition]


    # Sorting and storing the records based on the rating value
    most_rated = cond_rows.sort_values(by=['rating', 'effectiveness', 'sideEffects'], ascending=False)

    # List of Drug names for a particular condition given by the user
    drugs = [x for x in most_rated['urlDrugName']]  
    a = dict()
    if(len(drugs) == 0):
        return render_template('drugsList.html', data=None, condition=user_condition, eff=eff, side=side)
    for index, row in most_rated.iterrows():
        if row['urlDrugName'] not in a:
            a[row['urlDrugName']] = []
        t = {
      'rating': int(row['rating']),
        'effectiveness': row['effectiveness'],
        'sideEffects': row['sideEffects'],
        'condition' : row['condition'],
        'benefitsReview' : row['benefitsReview'],
        'sideEffectsReview' : row['sideEffectsReview']          
    }
        a[row['urlDrugName']].append(t)
    di = a
    
    return render_template('drugsList.html', data=di, condition = user_condition, eff=eff, side=side)

if __name__ == '__main__':
    app.run(debug=True)
