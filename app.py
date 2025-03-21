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

# -----------------admin dashboard routes-----------------

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
            chapter = Chapter.query.get_or_404(chapter_id)
            
            try:
                # Delete the chapter
                db.session.delete(chapter)
                db.session.commit()
                flash('Chapter deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the chapter.', 'danger')
               
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

# Route to add a quiz in quiz dashboard             
@app.route("/add_quiz", methods=['GET', 'POST'])
@app.route("/add_quiz/<int:chapter_id>", methods=['GET', 'POST'])
def add_quiz(chapter_id=None):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            chapters = Chapter.query.all()
            chapter = Chapter.query.get(chapter_id) if chapter_id else None

            if request.method == 'POST':
                name = request.form['name']
                date_str = request.form['date']
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                chapter_id = request.form.get('chapter_id') or chapter_id

                if not chapter_id:
                    flash('Please select a chapter.', 'warning')
                    return redirect(url_for('add_quiz'))

                existing_quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()
                if existing_quiz:
                    flash('Quiz already exists for this chapter', 'warning')
                    return redirect(url_for('quiz_dashboard'))

                new_quiz = Quiz(chapter_id=chapter_id, name=name, date=date)
                db.session.add(new_quiz)
                db.session.commit()
                flash('Quiz added successfully!', 'success')
                return redirect(url_for('quiz_dashboard'))

            return render_template("add_quiz.html", chapters=chapters, chapter=chapter)

        flash('You are not authorized to perform this action.', 'warning')
        return redirect(url_for('quiz_dashboard'))
    
    flash('Please log in to continue.', 'danger')
    return redirect(url_for('login'))



# Route to edit a quiz in quiz dashboard                                                  
@app.route("/edit_quiz/<int:quiz_id>", methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                flash("Quiz not found", "danger")
                return redirect(url_for("quiz_dashboard"))

            if request.method == 'POST':
                chapter_id = request.form['chapter_id']
                name = request.form['name']
                date_str = request.form['date']

                try:
                    quiz.chapter_id = int(chapter_id)
                    quiz.name = name
                    quiz.date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    db.session.commit()
                    flash("Quiz updated successfully", "success")
                    return redirect(url_for('quiz_dashboard'))

                except ValueError:
                    flash("Invalid input format. Ensure date is YYYY-MM-DD", "danger")

            chapters = Chapter.query.all()  # Fetch all chapters for dropdown
            return render_template("edit_quiz.html", quiz=quiz, chapters=chapters)

        else:
            flash("You are not authorized to edit quizzes", "danger")
            return redirect(url_for("quiz_dashboard"))
    else:
        flash("Please log in to access this page", "warning")
        return redirect(url_for("login"))

# Route to delete a quiz in quiz dashboard 
@app.route("/delete_quiz/<int:quiz_id>", methods=['POST'])
def delete_quiz(quiz_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            quiz = Quiz.query.get_or_404(quiz_id)
            try:
                db.session.delete(quiz)
                db.session.commit()
                flash('Quiz deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the quiz.', 'danger')
            return redirect(url_for('quiz_dashboard'))  # Redirect to quiz dashboard
        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('quiz_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

# Route to add a question in quiz dashboard 
@app.route("/add_question", methods=['GET', 'POST'])
@app.route("/add_question/<int:quiz_id>", methods=['GET', 'POST'])
def add_question(quiz_id=None):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            quizzes = Quiz.query.all()
            quiz = Quiz.query.get(quiz_id) if quiz_id else None

            if request.method == 'POST':
                title = request.form['title']
                question_text = request.form['question']
                option1 = request.form['option1']
                option2 = request.form['option2']
                option3 = request.form['option3']
                option4 = request.form['option4']
                answer = request.form['answer']
                quiz_id = int(request.form.get('quiz')) if request.form.get('quiz') else None

                print("Quiz ID:", quiz_id)  # Debugging

                if not quiz_id:
                    flash("Error: Quiz ID is missing.", "danger")
                    return redirect(url_for('add_question'))

                new_question = Question(
                    title=title,
                    question=question_text,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    answer=answer,
                    quiz_id=quiz_id
                )

                try:
                    db.session.add(new_question)
                    db.session.commit()
                    flash('Question added successfully!', 'success')
                    return redirect(url_for('quiz_dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding question: {str(e)}', 'danger')

            return render_template("add_question.html", quizzes=quizzes, quiz=quiz)

        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('quiz_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))


# Route to edit a question
@app.route("/edit_question/<int:question_id>", methods=['GET', 'POST'])
def edit_question(question_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            question = Question.query.get_or_404(question_id)
            quizzes = Quiz.query.all()
            
            if request.method == 'POST':
                question.title = request.form['title']
                question.question = request.form['question']
                question.option1 = request.form['option1']
                question.option2 = request.form['option2']
                question.option3 = request.form['option3']
                question.option4 = request.form['option4']
                question.answer = request.form['answer']
                question.quiz_id = request.form.get('quiz')  # Update quiz association

                try:
                    db.session.commit()
                    flash('Question updated successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error updating question.', 'danger')

                return redirect(url_for('quiz_dashboard'))

            return render_template("edit_question.html", question=question, quizzes=quizzes)  # Load form for editing question

        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('quiz_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))


# Route to delete a question
@app.route("/delete_question/<int:question_id>", methods=['POST'])
def delete_question(question_id):
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            question = Question.query.get_or_404(question_id)
            try:
                db.session.delete(question)
                db.session.commit()
                flash('Question deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error deleting question.', 'danger')

            return redirect(url_for('quiz_dashboard'))

        else:
            flash('You are not authorized to perform this action.', 'warning')
            return redirect(url_for('quiz_dashboard'))
    else:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))


    

# Route to add summary in admin dashboard
@app.route("/admin_summary")
def admin_summary():
    if "user" in session and session.get("role") == "admin":
        quiz_data = (
            db.session.query(
                Quiz.name,
                db.func.max(QuizAttempt.score).label("top_score"),
                db.func.count(QuizAttempt.id).label("attempts"),
            )
            .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)
            .group_by(Quiz.id)
            .all()
        )

        subjects = [quiz.name for quiz in quiz_data]
        top_scores = [quiz.top_score for quiz in quiz_data]
        attempts = [quiz.attempts for quiz in quiz_data]

        return render_template(
            "admin_summary.html",
            subjects=subjects,
            top_scores=top_scores,
            attempts=attempts
        )



 

if __name__ == "__main__":
    app.run(debug=True)

