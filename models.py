from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password = db.Column(db.String(40), unique=False, nullable=False)
    Name = db.Column(db.String(80), unique=False, nullable=False)
    Qualification = db.Column(db.String(80), unique=False, nullable=False)
    DOB = db.Column(db.String(80), unique=False, nullable=False)
    scores = db.relationship('Scores', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), unique=True, nullable=False)
    Description = db.Column(db.String(80), unique=False, nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), unique=True, nullable=False)
    Description = db.Column(db.String(80), unique=False, nullable=False)
    Subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_quiz = db.Date(db.String(80), unique=False, nullable=False)
    time_duration = db.Time(db.String(80), unique=False, nullable=False)
    Chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question',backref='Quiz', lazy=True)
    scores = db.relationship('Scores', backref='Quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Question = db.Column(db.String(80), unique=True, nullable=False)
    Option1 = db.Column(db.String(80), unique = True, nullable = False)
    Answer = db.column(db.String(80), unique = True, nullable = False)
    Quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp_of_quiz = db.Date(db.String(80), unique=False, nullable=False)
    total_scored = db.Column(db.Integer, unique=False, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user,id'), nullable = False)
    Quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)



