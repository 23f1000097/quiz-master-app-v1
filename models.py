from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(40), unique=False, nullable=False)
    confirm_password = db.Column(db.String(40), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    qualification = db.Column(db.String(80), unique=False, nullable=False)
    dob = db.Column(db.String(80), unique=False, nullable=False)
    role = db.Column(db.String(80), unique=False, nullable=False)
    scores = db.relationship('Scores', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    date = db.Column(db.Date(), unique=False, nullable=False)
    duration = db.Column(db.Time, unique=False, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question',backref='Quiz', lazy=True)
    scores = db.relationship('Scores', backref='Quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    question = db.Column(db.String(80), unique=True, nullable=False)
    option1 = db.Column(db.String(80), unique = True, nullable = False)
    answer = db.Column(db.String(80), unique = True, nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp_of_quiz = db.Column(db.Time, unique=False, nullable=False)
    total_scored = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)

