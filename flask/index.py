from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from csv import reader
from io import BytesIO
from pathlib import Path
import pyfpgrowth
import csv
import os
import pandas as pd


# os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__)
Bootstrap(app)

FILE_UPLOADS = './uploads'
app.config["FILE_UPLOADS"] = FILE_UPLOADS

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csv.db'
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    sup = db.Column(db.Integer)
    con = db.Column(db.Integer)
    result = db.Column(db.String(200))


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def home():
    #	myFiles = File.query.all()
    #	return render_template('index.html', myFiles=myFiles)
    return render_template('home.html')


@app.route('/data')
def data():
    myFiles = File.query.all()
    return render_template('data.html', myFiles=myFiles)
#	return render_template('data.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    #	path_parent = os.path.dirname(os.getcwd())
    #	os.chdir(path_parent)

    if request.method == "POST":

        if request.files:
            file = request.files['inputFile']
            support = request.form['support']
            confidence = request.form['confidence']

            file.save(os.path.join(app.config["FILE_UPLOADS"], file.filename))
            with open('./uploads/' + file.filename, newline='') as f:
                reader = csv.reader(f)
                data = list(reader)
                transactions = data
                patterns = pyfpgrowth.find_frequent_patterns(
                    transactions, len(transactions) * int(support)/100)
                rules = pyfpgrowth.generate_association_rules(
                    patterns, int(confidence)/100)
#                return str(rules)
            res = rules
            newFile = File(name=file.filename, sup=support,
                           con=confidence, result=res)

        db.session.add(newFile)
        db.session.commit()
        return render_template("data.html", result=result)

    # return 'Saved ' + file.filename + 'to the database!'

#	return redirect(url_for('home'))


@app.route("/delete/<id>/", methods=["GET"])
def delete(id):
    my_data = File.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/proses/<id>/", methods=["GET"])
def proses(id):
    my_data = File.query.get(id)
    with open('./uploads/' + my_data.name, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        transactions = data
        patterns = pyfpgrowth.find_frequent_patterns(
            transactions, len(transactions) * my_data.sup/100)
        rules = pyfpgrowth.generate_association_rules(patterns, 0.5)
        return str(rules)

# Route for handling the login page logic


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('you were just logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('you were just logged out!')
    return redirect(url_for('welcome'))


if __name__ == '__name__':
    app.run(debug=True)
