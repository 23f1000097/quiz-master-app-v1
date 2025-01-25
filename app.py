from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User,Subject,Chapter,Quiz,Question,Scores
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

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
                print('Incorrect password') # shld flash this
                return redirect(url_for('home'))
        else:
            print('User not found') # shld flash this
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
            print('User already exists, please login') # shld flash this    
            return redirect(url_for('home'))
        if confirm_password != password: 
            print('Passwords do not match')
            return redirect(url_for('home'))
        new_user = User(name=name, username=username, password=password,confirm_password=confirm_password, qualification=qualification, dob=dob, role='user')
        db.session.add(new_user)
        db.session.commit()
        print('User registered successfully')  # shld flash this   
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
                return render_template("subject.html")
            elif request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                subject = Subject.query.filter_by(name=name).first()
                if subject:
                    print('Subject already exists')
                    return redirect(url_for('admin_dashboard'))
                else:
                    new_subject = Subject(name=name, description=description)
                    db.session.add(new_subject)
                    db.session.commit()
                    print('Subject added successfully')
                    return redirect(url_for('admin_dashboard'))
            

        else:
            flash('You are not authorized to view this page')





# Route to add a chapter in admin dashboard
@app.route("/add_chapter", methods=['GET', 'POST'])
def add_chapter():
    if 'user' in session:
        role = session.get('role')
        if role == 'admin':
            if request.method == 'GET':
                subjects = Subject.query.all()
                subject_id = request.args.get('subject_id')
                return render_template("chapter.html", subjects=subjects)

            elif request.method == 'POST':
                name = request.form['name']
                description = request.form['description']
                chapter = Chapter.query.filter_by(name=name).first()
                if chapter:
                    print('Chapter already exists')
                    return redirect(url_for('admin_dashboard'))
                else:
                    new_chapter = Chapter(name=name, description=description)
                    db.session.add(new_chapter)
                    db.session.commit()
                    print('Chapter added successfully')
                    return redirect(url_for('admin_dashboard'))
        else:

            flash('You are not authorized to view this page')

#

# Route to add a quiz in admin dashboard
@app.route("/add_quiz", methods=['GET', 'POST'])
def add_quiz():
    # if 'user' in session:
    #     role = session.get('role')
    #     if role == 'admin':
    #         if request.method == 'GET':
    #             chapters = Chapter.query.all()
    #             return render_template("quiz.html", chapters=chapters)
    #         elif request.method == 'POST':
    #             name = request.form['name']
    #             description = request.form['description']
    #             chapter_id = request.form['chapter_id']
    #             quiz = Quiz.query.filter_by(name=name).first()
    #             if quiz:
    #                 print('Quiz already exists')
    #                 return redirect(url_for('admin_dashboard'))
    #             else:
    #                 new_quiz = Quiz(name=name, description=description, chapter_id=chapter_id)
    #                 db.session.add(new_quiz)
    #                 db.session.commit()
    #                 print('Quiz added successfully')
    #                 return redirect(url_for('admin_dashboard'))
    #     else:
    #         flash('You are not authorized to view this page')
    return render_template("quiz.html")

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

