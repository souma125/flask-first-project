from flask import Flask, render_template, jsonify, session, request, flash, redirect, url_for,sessions
from sqlalchemy import create_engine, text, exc
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
import sys
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors
import re
import hashlib
app = Flask(__name__)
# csrf = CSRFProtect(app)
# Set a secret key
app.secret_key = 'fsdfsdf sdfdsqw'
engine = create_engine(
    "mysql+pymysql://root:@localhost/parineetas_career?charset=utf8mb4")

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'parineetas_career'
# Intialize MySQL
mysql = MySQL(app)


def fetch_jobs_with_cursor():
    with engine.connect() as connection:
        query = text("SELECT * FROM `jobs`")
        cursor = connection.execute(query)
        jobs_list = []

        # Get the column names from result keys
        columns = cursor.keys()

        for row in cursor:
            job_dict = dict(zip(columns, row))
            jobs_list.append(job_dict)

        return jobs_list


def load_job_details_from_db(id):
    with engine.connect() as connection:
        query = text("SELECT * FROM `jobs` where id = :val")
        cursor = connection.execute(query, {"val": id})
        # rows = cursor.all()
        # if len(rows) == 0:
        #     return None
        # else:
        #     return dict(rows[0])
        job_details = []
        columns = cursor.keys()
        for row in cursor:
            job_details_dict = dict(zip(columns, row))
            job_details.append(job_details_dict)
        return job_details

@app.route('/')
def home():
    JOBS = fetch_jobs_with_cursor()

    return render_template('home.html', jobs=JOBS, company_name='Parineeta')


@app.route('/jobs/<id>')
def jobs_details(id):
    job_details = load_job_details_from_db(id)

    return render_template('job_details.html', job_details=job_details, job_id=id,)


@app.route('/application-form', methods=['GET', 'POST'])
def application_form():
    if request.method == 'POST':
        job_id = request.form.get('job_id')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        linkedin_url = request.form.get('linkedin_url')
        education = request.form.get('education')
        work_experience = request.form.get('work_experience')
        resume_url = request.files['resume_url']
        if full_name == '':
            flash('Please enter valid full name', category='error')
        elif email == '':
            flash('Please enter a valid email', category='error')
        elif linkedin_url == '':
            flash('Please enter a valid linkedin_url', category='error')
        elif education == '':
            flash('Please enter a valid education', category='error')
        elif work_experience == '':
            flash('Please enter a valid work_experience', category='error')
        elif resume_url == '':
            flash('Please enter a valid resume', category='error')
        else:
            if 'resume_url' in request.files:
                resume_file = request.files['resume_url']
                upload_folder = 'uploads'
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, resume_file.filename)
                resume_file.save(file_path)
                insert_query = text("INSERT INTO applications (job_id,full_name, email, linkedin_url, education, work_experience,resume_url) "
                                    "VALUES (:job_id,:full_name, :email, :linkedin_url, :education, :work_experience,:resume_url)")
                try:
                    with engine.connect() as conn:
                        conn.execute(insert_query, {
                            'job_id': job_id,
                            'full_name': full_name,
                            'email': "email",
                            'linkedin_url': "linkedin_url",
                            'education': education,
                            'work_experience': work_experience,
                            'resume_url': file_path
                        })
                        conn.commit()
                        flash('Application created successfully',
                              category='success')
                        return redirect(url_for('jobs_details', id=job_id))
                except exc.SQLAlchemyError as e:
                    flash(str(e), category="error")
                    return redirect(url_for('jobs_details', id=job_id))
    else:
        flash("Something went wrong", category="error")
        return redirect(url_for('jobs_details', id=job_id))


@app.route('/login/', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/user_login', methods=['POST','GET'])
def user_login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password_1 = request.form.get('password')
        hash = password_1 + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        cursor = mysql.connection.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s',(username,password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home',session = session))
        else:
            flash('not valid details',category='error')
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return redirect(url_for('home'))

@app.route('/register/', methods=['GET','POST'])
def register():
    return render_template('register.html')
@app.route('/user_registration',methods=['POST','GET'])
def user_registration():
    if request.method== 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        email = request.form.get('email')
        username = request.form.get('username')
        password_1 = request.form.get('password')
        if email == '':
             flash('Please enter a valid email', category='error')
        elif username == '':
            flash('Please enter a valid username', category='error')
        elif password_1 == '':
            flash('Please enter a valid password_1', category='error')
        else:
            hash = password_1 + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO accounts VALUES (NULL,%s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            return redirect(url_for('login'))
        return redirect(url_for('register'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
