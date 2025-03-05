from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User,Subject,Chapter,Quiz,Question,Scores
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trishaa.sqlite'
app.config['SECRET_KEY'] = 'my_secret_key'
db.init_app(app)

def create_admin():
    admin = User.query.filter_by(username='admin@gmail.com').first()
    if not admin:
        admin = User(name='admin', username='admin@gmail.com', password='1234',confirm_password='1234', qualification='admin', dob='11-02-2005', role='admin')
        db.session.add(admin)
        db.session.commit()

with app.app_context():
    db.create_all()
    create_admin()

# Route to render the login page
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['user'] = user.username
                session['role'] = user.role
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password') 
                return redirect(url_for('home'))
        else:
            flash('User not found')
            return redirect(url_for('home'))


# Route to render the New user register template
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        qualification = request.form['qualification']
        dob = request.form['dob']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists, please login')    
            return redirect(url_for('home'))
        if confirm_password != password: 
            flash('Passwords do not match')
            return redirect(url_for('home'))
        new_user = User(name=name, username=username, password=password,confirm_password=confirm_password, qualification=qualification, dob=dob, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully')  
        return redirect(url_for('dashboard'))

# Route to render the dashboard 
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session: # the user is a key in the session dictionary, if it is present, the user is logged in
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("user_dashboard.html")
    else:
        flash('Please login to continue')
        return redirect(url_for('home'))

# Route to render the admin dashboard
@app.route("/admin_dashboard", methods=['GET', 'POST'])
def admin_dashboard():
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            subjects = Subject.query.all()
            return render_template("admin_dashboard.html", subjects=subjects)
        else:
            flash('You are not authorized to view this page')
            return redirect(url_for('home'))
    else:
        flash('Please login to continue')
        return redirect(url_for('home'))
        
# Route to add a subject in admin dashboard
@app.route("/add_subject", methods=['GET', 'POST'])
def add_subject():
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                return render_template("add_subject.html")
            elif request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                subject = Subject.query.filter_by(name=name).first()
                if subject:
                    flash('Subject already exists', 'warning')
                    return redirect(url_for('admin_dashboard'))
                else:
                    new_subject = Subject(name=name, description=description)
                    db.session.add(new_subject)
                    db.session.commit()
                    flash('Subject added successfully', 'success')
                    return redirect(url_for('admin_dashboard'))
            

        else:
            flash('You are not authorized to view this page', 'danger')

# Route to edit a subject in admin dashboard
@app.route("/edit_subject/<int:subject_id>", methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                subject = Subject.query.get_or_404(subject_id)
                return render_template("edit_subject.html", subject=subject)
            elif request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                subject = Subject.query.get_or_404(subject_id)
                subject.name = name
                subject.description = description
                db.session.commit()
                flash('Subject updated successfully', 'success')
                return redirect(url_for('admin_dashboard'))
        else:
            flash('You are not authorized to view this page', 'danger')
            return redirect(url_for('home'))
    else:
        flash('Please login to continue', 'alert')
        return redirect(url_for('home'))

# Route to delete a subject in admin dashboard
@app.route("/delete_subject/<int:subject_id>", methods=['POST'])
def delete_subject(subject_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            subject = Subject.query.get_or_404(subject_id)
            
            try:
                db.session.delete(subject)
                db.session.commit()
                flash('Subject deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the subject.', 'danger')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('admin_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))




# Route to add a chapter in admin dashboard
@app.route("/add_chapter", methods=['GET', 'POST'])
@app.route("/add_chapter/<int:subject_id>", methods=['GET', 'POST'])
def add_chapter(subject_id=None):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                subjects = Subject.query.all()
                if subject_id:
                    # If subject_id is provided in the URL, fetch the specific subject
                    subject = Subject.query.get_or_404(subject_id)
                    return render_template("add_chapter.html", subject=subject, subjects=subjects)
                else:
                    # If no subject_id in the URL, just show the dropdown with all subjects
                    return render_template("add_chapter.html", subjects=subjects)
            elif request.method == 'POST':
                name = request.form.get('name')
                description = request.form.get('description')
                subject_id = request.form.get('subject')  # subject_id from form

                # Check if the chapter already exists
                chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
                if chapter:
                    flash('Chapter already exists', 'warning')
                    return redirect(url_for('admin_dashboard'))
                else:
                    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
                    db.session.add(new_chapter)
                    db.session.commit()
                    flash('Chapter added successfully', 'success')
                    return redirect(url_for('admin_dashboard'))

# Route to edit a chapter in admin dashboard
@app.route("/edit_chapter/<int:subject_id>/<int:chapter_id>", methods=['GET', 'POST'])
def edit_chapter(subject_id, chapter_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                chapter = Chapter.query.filter_by(id=chapter_id, subject_id=subject_id).first_or_404()
                return render_template("edit_chapter.html", chapter=chapter)
            elif request.method == 'POST':
                name = request.form['name']
                description = request.form['description']

                chapter = Chapter.query.filter_by(id=chapter_id, subject_id=subject_id).first_or_404()
                
                # Update chapter details
                chapter.name = name
                chapter.description = description
                db.session.commit()
                print('Chapter updated successfully')
                return redirect(url_for('admin_dashboard'))
        else:
            flash('You are not authorized to view this page')
            return redirect(url_for('login'))
    else:
        flash('Please log in first')
        return redirect(url_for('login'))

# Route to delete a chapter in admin dashboard
@app.route("/delete_chapter/<int:chapter_id>", methods=['POST'])
def delete_chapter(chapter_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            # Fetch the chapter by ID
            chapter = Chapter.query.get_or_404(chapter_id)
            
            try:
                # Delete the chapter
                db.session.delete(chapter)
                db.session.commit()
                flash('Chapter deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the chapter.', 'danger')
                print(e)
                
            return redirect(url_for('admin_dashboard'))
        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('admin_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))
                
                

# Route for quiz dashboard
@app.route("/quiz_dashboard", methods=['GET', 'POST'])
def quiz_dashboard():
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            quizzes = Quiz.query.all()
            return render_template("quiz_dashboard.html", quizzes=quizzes)
        else:
            flash('You are not authorized to view this page')
            return redirect(url_for('home'))
    else:
        flash('Please login to continue')
        return redirect(url_for('home'))
            

# Route to add a quiz in admin dashboard
@app.route("/add_quiz", methods=['GET', 'POST'])
def add_quiz():
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                chapters = Chapter.query.all()
                return render_template("add_quiz.html", chapters=chapters) 
            elif request.method == 'POST':
                chapter_id = request.form['chapter_id']
                name = request.form['name']
                date_str = request.form['date']
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                duration_str = request.form['duration']
                duration = datetime.strptime(duration_str, '%M:%S').time()
                quiz = Quiz.query.filter_by(chapter_id=chapter_id).first() 
                if quiz:
                    flash('Quiz already exists')
                    return redirect(url_for('quiz_dashboard'))
                else:
                    new_quiz = Quiz(chapter_id=chapter_id, name=name, date=date, duration=duration)
                    db.session.add(new_quiz)
                    db.session.commit()
                    print('Quiz added successfully')
                    return redirect(url_for('quiz_dashboard'))
        else:
            flash('You are not authorized to view this page')

# Route to add a question in quiz dashboard 
@app.route("/add_question", methods=['GET', 'POST'])
@app.route("/add_question/<int:quiz_id>", methods=['GET', 'POST'])
def add_question(quiz_id=None):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                quizzes = Quiz.query.all()
                chapters = Chapter.query.all()
                if quiz_id:
                    # If quiz_id is provided in the URL, fetch the specific quiz
                    quiz= Quiz.query.get_or_404(quiz_id)
                    return render_template("add_quiz.html", quiz=quiz, quizzes=quizzes, chapters=chapters)
                else:
                    # If no quiz_id in the URL, just show the dropdown with all subjects
                    return render_template("add_quiz.html", quizzes=quizzes, chapter=chapter)
            elif request.method == 'POST':
                chapter_id = request.form.get('chapter_id')
                date = request.form.get('date')
                duration = request.form.get('duration')
                quiz_id = request.form.get('quiz')  # quiz_id from form

                # Check if the quiz already exists
                quiz = Quiz.query.filter_by(date=date, quiz_id=quiz_id).first()
                if quiz:
                    print('Quiz already exists')
                    return redirect(url_for('quiz_dashboard'))
                else:
                    new_quiz = Quiz(chapter_id=chapter_id, date=date, duration=duration)
                    db.session.add(new_quiz)
                    db.session.commit()
                    print('Quiz added successfully')
                    return redirect(url_for('quiz_dashboard'))
    

# Route to add summary in admin dashboard
@app.route("/add_summary", methods=['GET', 'POST'])
def add_summary():
    # if 'user' in session:
    #     role = session.get('role')
    #     if role == 'admin':
    #         if request.method == 'GET':
    #             return render_template("summary.html")
    #         elif request.method == 'POST':
    #             name = request.form['name']
    #             description = request.form['description']
    #             summary = Summary.query.filter_by(name=name).first()
    #             if summary:
    #                 print('Summary already exists')
    #                 return redirect(url_for('admin_dashboard'))
    #             else:
    #                 new_summary = Summary(name=name, description=description)
    #                 db.session.add(new_summary)
    #                 db.session.commit()
    #                 print('Summary added successfully')
    #                 return redirect(url_for('admin_dashboard'))
    #     else:
    #         flash('You are not authorized to view this page')
    return render_template("summary.html")
 

if __name__ == "__main__":
    app.run(debug=True)

