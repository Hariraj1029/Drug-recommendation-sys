from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1029@localhost:3306/drug-recommendation'
db = SQLAlchemy(app)


class Review(db.Model):
    revId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drugName = db.Column(db.String(80),
                         nullable=False)
    condition = db.Column(db.String(120), unique=False, nullable=False)
    commentsReview = db.Column(db.String(5000), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    sideEffects = db.Column(db.Integer, unique=False, nullable=False)
    sideEffectsReview = db.Column(db.String(5000), unique=False, nullable=False)
    effectiveness = db.Column(db.Integer, unique=False, nullable=False)
    benefitsReview = db.Column(db.String(5000), unique=False, nullable=False)
    sideEffectsKeywords = db.Column(
        db.String(500), unique=False, nullable=False)
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


with app.app_context():
    db.create_all()  # creating tables
