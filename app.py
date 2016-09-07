import os
import os.path
import time
import cPickle
import datetime
import flask
import tornado.wsgi
import tornado.httpserver

import urllib
import sqlite3

# Obtain the flask app object
app = flask.Flask(__name__)

DATABASE_NAME = "./databases/pega_ds.db"

#Advertising Data Table Columns
TABLE_ADVERTISING_DATA ="adsData"
KEY_ADVERTISING_ID = "ads_id"
KEY_ADVERTISING_NAME = "ads_name"
KEY_ADVERTISING_DURATION = "ads_duration"
KEY_ADVERTISING_PLAYBACK_COUNT = "ads_playback_count"
KEY_ADVERTISING_PLAYBACK_FIRST_DATE = "first_playback_date"
KEY_ADVERTISING_PLAYBACK_LAST_DATE = "last_playback_date"

#Personal Data Table Columns
TABLE_PERSONAL_DATA ="personalData"
KEY_PERSONAL_ID = "personal_id"
KEY_PERSONAL_FACE_FEATURES = "face_features"
KEY_PERSONAL_GENDER = "gender"
KEY_PERSONAL_AGE = "age"
KEY_PERSONAL_CAR = "car_brand"

#Viewing Data Table Columns
TABLE_VIEWING_DATA ="viewingData"
KEY_VIEWING_ID = "viewing_id"
KEY_VIEWING_ADS_ID = KEY_ADVERTISING_ID
KEY_VIEWING_PERSONAL_ID = KEY_PERSONAL_ID
KEY_VIEWING_TIME = "viewing_time"
KEY_VIEWING_DATE = "viewing_date"

#Person Counting Table Columns
TABLE_PERSON_COUNTING_DATA ="personCountingData"
KEY_PERSON_COUNTING_ID = "person_counting_id";
KEY_PERSON_COUNTING_ADS_ID = KEY_ADVERTISING_ID
KEY_PERSON_COUNT = "person_count"
KEY_PERSON_COUNTING_UPDATE_DATE = "update_date"

GENDER_LIST = ("Male", "Female")
AGE_LIST = ("0 ~ 2", "4 ~ 6", "8 ~ 12", "13 ~ 17", "18 ~ 24", "25 ~ 34", "35 ~ 44", "45 ~ 54", "55 ~ 64", "65+")

@app.route('/')
def index():
    if os.path.isfile(DATABASE_NAME):
        print "Database exists"
    else:
        print "Database not exists!"
        return flask.render_template(
            'index.html', has_result=False
        )

    person_counting_data = fetch_latest_person_counting_data()
    ads_data = None
    if person_counting_data is None:
        return flask.render_template(
            'index.html', has_result=False
        )
    else:
        ads_id = person_counting_data[1]
        ads_data = fetch_ads_data(ads_id)
        print ads_data

    viewing_datas = fetch_latest_viewing_datas()

    if (viewing_datas is None) or (len(viewing_datas) == 0):
        return flask.render_template(
            'index.html', has_result=True, has_viewing_data=False,
            ads_data=ads_data,
            person_counting_data=person_counting_data
        )
    else:
        ads_datas = []
        personal_datas = []
        print viewing_datas
        for i in range(len(viewing_datas)):
            personal_id = viewing_datas[i][2]
            personal_data = fetch_personal_data(personal_id)

            personal_datas.append((GENDER_LIST[personal_data[2]], AGE_LIST[personal_data[3]], personal_data[4]))
            print personal_datas

        return flask.render_template(
            'index.html', has_result=True, has_viewing_data=False,
            ads_data=ads_data,
            person_counting_data=person_counting_data,
            viewing_datas=viewing_datas,
            personal_datas=personal_datas
        )


def fetch_latest_viewing_datas():
    viewing_datas = None
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        c = connection.cursor()

        c.execute("""
        SELECT * FROM viewingData WHERE viewing_date = (SELECT MAX(viewing_date) FROM viewingData)
        """)

        viewing_datas = c.fetchall()

    except sqlite3.Error as err:
        viewing_datas = None
        print 'An error occurred: ', err

    return viewing_datas

def fetch_latest_person_counting_data():
    counting_data = None
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        c = connection.cursor()

        c.execute("""
        SELECT * FROM personCountingData WHERE update_date = (SELECT MAX(update_date) FROM personCountingData)
        """)

        data = c.fetchall()
        counting_data = data[0]

    except sqlite3.Error as err:
        counting_data = None
        print 'An error occurred: ', err

    return counting_data

def fetch_ads_data(ads_id):
    ads_data = None
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        c = connection.cursor()

        query = """
            SELECT * FROM %s 
            WHERE %s=%d """ % (
            TABLE_ADVERTISING_DATA, KEY_ADVERTISING_ID, ads_id)

        c.execute(query)

        data = c.fetchall()
        ads_data = data[0]

    except sqlite3.Error as err:
        ads_data = None
        print 'An error occurred: ', err

    return ads_data


def fetch_personal_data(personal_id):
    personal_data = None
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        c = connection.cursor()

        query = """
            SELECT * FROM %s 
            WHERE %s=%d """ % (
            TABLE_PERSONAL_DATA, KEY_PERSONAL_ID, personal_id)

        c.execute(query)

        data = c.fetchall()
        personal_data = data[0]

    except sqlite3.Error as err:
        personal_data = None
        print 'An error occurred: ', err

    return personal_data


def start_tornado(app, port=9000):
    http_server = tornado.httpserver.HTTPServer(
        tornado.wsgi.WSGIContainer(app))
    http_server.listen(port)
    print("Tornado server starting on port {}".format(port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5000)
    start_tornado(app)
