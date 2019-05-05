import ConfigParser
import os
import sys
import hashlib
from flask import (Flask, flash, jsonify, render_template,
                   request, redirect, url_for)

from connection import session
from database_setup import DuesRecord

from create_db import main as update_database

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    name = ''
    due = ''
    result = ''
    DATE = fetchLastUpdateDetails()
    PAYMENT_DATE = fetchLastPaymentUpdateDetails()
    if request.method == 'GET':
        return render_template(
            'homepage.html',
            result=result,
            date=DATE,
            paymentdate=PAYMENT_DATE)
    elif request.method == 'POST':
        roll_no = request.form['roll_no'].encode('ascii').upper()
        try:
            record = session.query(DuesRecord).filter_by(roll_no=roll_no).one()
            name, due = record.name, record.due
            return render_template(
                'homepage.html',
                name=name,
                due=due,
                result='',
                date=DATE,
                paymentdate=PAYMENT_DATE)
        except BaseException:
            result = "Invalid roll number!"
            return render_template(
                'homepage.html',
                name='NA',
                due=0,
                result=result,
                date=DATE,
                paymentdate=PAYMENT_DATE)
    else:
        pass


@app.route('/<roll_no>')
def homepageJSON(roll_no):
    roll_no = roll_no.encode('ascii').upper()
    try:
        record = session.query(DuesRecord).filter_by(roll_no=roll_no).one()
        return jsonify(due=record.serialize)
    except BaseException:
        return '''
                Format:    hostel-dues.herokuapp.com/<roll_no>
                <br/>
                Example:   hostel-dues.herokuapp.com/b150487cs
               '''


@app.route('/update', methods=['GET', 'POST'])
def updateDatabase():
    if request.method == 'GET':
        DATE = fetchLastUpdateDetails()
        PAYMENT_DATE = fetchLastPaymentUpdateDetails()
        return render_template(
            'updatepage.html',
            date=DATE,
            paymentdate=PAYMENT_DATE)
    elif request.method == 'POST':
        if 'password' in request.form:
            if checkPassword(request.form['password']):
                update_database()
            return redirect(url_for('homepage'))
    else:
        pass


def fetchLastUpdateDetails():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    day = config.get('Last_Update', 'date')
    month = config.get('Last_Update', 'month')
    year = config.get('Last_Update', 'year')
    return day + '/' + month + '/' + year


def fetchLastPaymentUpdateDetails():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    day = config.get('Last_Payment_Update', 'date')
    month = config.get('Last_Payment_Update', 'month')
    year = config.get('Last_Payment_Update', 'year')
    return day + '/' + month + '/' + year


def checkPassword(value):
    return hashlib.sha256(value).hexdigest().upper() \
        == '2DC4C7DC156D0183B2E1783176289137BC9CB2829E98D48094087557EEE09B71'


def main():
    fetchLastUpdateDetails()
    fetchLastPaymentUpdateDetails()
    app.secret_key = 'theQuickBrownFoxJumpsOverTheLazyDog'
    if len(sys.argv) > 1:
        if sys.argv[1] == 't':
            app.debug = True
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
