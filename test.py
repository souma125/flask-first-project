from flask import Flask, render_template, jsonify, session, request, flash, redirect, url_for
from sqlalchemy import create_engine, text, exc
from flask_mail import Mail
app = Flask(__name__)
# Set a secret key
app.secret_key = 'fsdfsdf sdfdsqw'
engine = create_engine(
    "mysql+pymysql://root:@localhost/parineetas_career?charset=utf8mb4")

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for SMTP SSL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'sarkar.mayuri211098@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

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
def hello():
    JOBS = fetch_jobs_with_cursor()

    return render_template('home.html', jobs=JOBS, company_name='Parineeta')


@app.route('/jobs/<id>')
def jobs_details(id):
    job_details = load_job_details_from_db(id)
    # return jsonify(job_details)
    return render_template('job_details.html', job_details=job_details, job_id=id)


@app.route('/application-form', methods=['POST'])
def application_form():
    if request.method == 'POST':
        job_id = request.form.get('job_id')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        linkedin_url = request.form.get('linkedin_url')
        education = request.form.get('education')
        work_experience = request.form.get('work_experience')
        resume_url = request.form.get('resume_url')

        if len(full_name) < 2:
            flash("Please enter a valid First Name", category="error")
        elif len(email) < 2:
            flash("Please enter a valid email", category="error")
        elif len(linkedin_url) < 2:
            flash("Please enter a valid linkedin url", category="error")
        elif len(education) < 2:
            flash("Please enter a valid education", category="error")
        elif len(work_experience) < 0:
            flash("Please enter a valid work_experience", category="error")
        elif resume_url == '':
            flash("Please enter a valid resume_url", category="error")
        else:
            insert_query = text("INSERT INTO applications (job_id,full_name, email, linkedin_url, education, work_experience,resume_url) "
                                "VALUES (:job_id,:full_name, :email, :linkedin_url, :education, :work_experience,:resume_url)")

            try:
                with engine.connect() as connection:
                    connection.execute(insert_query,
                                       {
                                           'job_id': job_id,
                                           'full_name': full_name,
                                           'email': email,
                                           'linkedin_url': linkedin_url,
                                           'education': education,
                                           'work_experience': work_experience,
                                           'resume_url': resume_url
                                       })
                    connection.commit()
                # If no exceptions were raised, the INSERT was successful
                flash('Application created successfully', category='success')
                return redirect(url_for('jobs_details', id=job_id))

            except exc.SQLAlchemyError as e:
                # Handle any exceptions that may occur during the INSERT
                # return f'Error: {str(e)}'
                flash(str(e), category="error")
                return redirect(url_for('jobs_details', id=job_id))

    flash("Form method should be post", category="error")
    return redirect(url_for('jobs_details', id=job_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
