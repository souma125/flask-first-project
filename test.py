from flask import Flask, render_template,jsonify
app = Flask(__name__)
JOBS = [
    {
        'id': 1,
        'title':'Django Devloper',
        'location': 'Kolkata',
        'Salary': 'Rs. 100000'
    },
    {
        'id': 2,
        'title':'Python Devloper',
        'location': 'Bangaluru',
        'Salary': 'Rs. 100000'
    },
    {
        'id': 3,
        'title':'AI Devloper',
        'location': 'Pune',
        'Salary': 'Rs. 200000'
    }
]
@app.route('/')
def hello():
    return render_template('home.html',jobs=JOBS, company_name = 'Parineeta')

@app.route('/jobs')
def jobs():
    return jsonify(JOBS)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)