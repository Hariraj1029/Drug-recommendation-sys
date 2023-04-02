import pandas as pd
from flask import Flask, session, render_template, request, redirect, url_for
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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
    drugName = db.Column(db.String(80), nullable=False)
    condition = db.Column(db.String(120), unique=False, nullable=False)
    commentsReview = db.Column(db.String(5000), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    sideEffects = db.Column(db.Integer, unique=False, nullable=False)
    sideEffectsReview = db.Column(db.String(5000), unique=False, nullable=False)
    effectiveness = db.Column(db.Integer, unique=False, nullable=False)
    benefitsReview = db.Column(db.String(5000), unique=False, nullable=False)
    sideEffectsKeywords = db.Column(db.String(500), unique=False, nullable=False)
    benefits_review_sentiment_score = db.Column(db.Float, unique=False, nullable=False)
    sideEffects_review_sentiment_score = db.Column(db.Float, unique=False, nullable=False)
    comments_sentiment_score = db.Column(db.Float, unique=False, nullable=False)
    benefits_sentiment = db.Column(db.Integer, unique=False, nullable=False)
    sideEffects_sentiment = db.Column(db.Integer, unique=False, nullable=False)
    comments_sentiment = db.Column(db.Integer, unique=False, nullable=False)


class User(db.Model):
    email = db.Column(db.String(80), unique=True,
                      nullable=False, primary_key=True)
    password = db.Column(db.String(120), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)

env = Environment()
env.globals['int'] = int

# Read the CSV file data
df = pd.read_csv('total.csv')



@app.route('/upload')
def upload():

    # Iterate the CSV file and insert data into MySQL database
    for index, row in df.iterrows():
        record = Review(drugName=str(row['urlDrugName']),
                        condition=str(row['condition']),
                        commentsReview=str(row['commentsReview']),
                        rating=row['rating'],
                        sideEffects=row['sideEffects'],
                        sideEffectsReview=str(row['sideEffectsReview']),
                        effectiveness=row['effectiveness'],
                        benefitsReview=str(row['benefitsReview']),
                        sideEffectsKeywords=str(row['se_keywords']),
                        benefits_review_sentiment_score=row['benefits_review_sentiment_score'],
                        sideEffects_review_sentiment_score=row['sideEffects_review_sentiment_score'],
                        comments_sentiment_score=row['comments_sentiment_score'],
                        benefits_sentiment=row['benefits_sentiment'],
                        sideEffects_sentiment=row['sideEffects_sentiment'],
                        comments_sentiment=row['comments_sentiment'])
        db.session.add(record)
    db.session.commit()

    return 'File uploaded successfully'

def calc_sentiment(benefitsReview, sideEffectsReview, commentsReview):

    # Initialize the sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(benefitsReview)
    res=0
    if(scores['pos']> max(scores['neg'],scores['neu'])):
        res = 1
    elif(scores['neg']> max(scores['pos'],scores['neu'])):
        res = -1
    else:
        res = 0

    brss = scores['pos']*100
    bs = res

    scores = sia.polarity_scores(sideEffectsReview)
    res=0
    if(scores['pos']> max(scores['neg'],scores['neu'])):
        res = 1
    elif(scores['neg']> max(scores['pos'],scores['neu'])):
        res = -1
    else:
        res = 0

    srss = scores['pos']*100
    ss = res

    scores = sia.polarity_scores(commentsReview)
    res=0
    if(scores['pos']> max(scores['neg'],scores['neu'])):
        res = 1
    elif(scores['neg']> max(scores['pos'],scores['neu'])):
        res = -1
    else:
        res = 0

    css = scores['pos']*100
    cs = res
    return brss, srss, css, bs, ss, cs

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
        brss, srss, css, bs, ss, cs = calc_sentiment(benefitsReview, sideEffectsReview, commentsReview)
        entry = Review(drugName=drugName,
                       condition=condition,
                       commentsReview=commentsReview,
                       rating=rating,
                       sideEffects=sideEffects,
                       sideEffectsReview=sideEffectsReview,
                       effectiveness=effectiveness,
                       benefitsReview=benefitsReview,
                       sideEffectsKeywords=sideEffectsKeywords,
                       benefits_review_sentiment_score=brss,
                       sideEffects_review_sentiment_score=srss,
                       comments_sentiment_score=css,
                       benefits_sentiment=bs,
                       sideEffects_sentiment=ss,
                       comments_sentiment=cs)
        db.session.add(entry)
        db.session.commit()
    return render_template('index.html', username=session['username'])


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
    return render_template('addrev.html', username=session['username'])


# API endpoint to send the data
@app.route('/searched', methods=['POST'])
def getDrugs():
    with app.app_context():
        # print(data)
        # Do something with the data
        user_condition = request.form.get('search')
        most_rated = Review.query.order_by(
            Review.rating.desc(), Review.sideEffects.desc(), Review.effectiveness.desc(), Review.benefits_review_sentiment_score.desc(), Review.sideEffects_review_sentiment_score.desc()).filter_by(condition=user_condition).all()
        # Getting the rows which are having rating > 5 and also satisfied the user condition


        # Sorting and storing the records based on the rating values

        # List of Drug names for a particular condition given by the user
        drugs = Review.query.filter_by(condition=user_condition).with_entities(
            Review.drugName).distinct().all()
        a = dict()
        if(len(drugs) == 0):
            return render_template('drugsList.html', data=None, condition=user_condition, username=session['username'])
        for row in most_rated:
            if row.drugName not in a:
                a[row.drugName] = []
            t = {
        'rating': int(row.rating),
            'effectiveness': row.effectiveness,
            'sideEffects': row.sideEffects,
            'condition' : row.condition,
            'benefitsReview' : row.benefitsReview,
            'sideEffectsReview' : row.sideEffectsReview        
        }
            a[row.drugName].append(t)
        di = a
        
        return render_template('drugsList.html', data=di, condition = user_condition)

with app.app_context():
    conList = [x[0] for x in set(Review.query.with_entities(Review.condition).all())]
@app.route('/')
def home():
    return render_template('index.html', conList=conList)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
