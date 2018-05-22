import json
from flask import Flask, request, make_response, jsonify
import psycopg2
#from datetime import datetime

# Flask app should start in global layout
app = Flask(__name__)
log = app.logger


@app.route('/', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    #res = "Hurray!"

    if action == 'isValidDoctor':
        res = is_valid_doctor(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)

    return make_response(jsonify({'fulfillmentText': res}))

def is_valid_doctor(req):
    """Returns a string containing text with a response to the user
    with the weather forecast or a prompt for more information
    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """

    date1 = req['queryResult']['parameters']['date']
    date1 = ''.join(date1)
    date1 = date1[:10]

    # d1 = datetime.strptime(date1, '%Y-%m-%d')
    # # day_string = d1.strftime('%Y-%m-%d')
    #
    # now = datetime.now()
    # d2 = datetime.strptime(now, '%Y-%m-%d')



    doctor_name = req['queryResult']['parameters']['doctor_name']
    doctor_name = ''.join(doctor_name)
    doctor_name = doctor_name.strip().title()


    conn = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()
    response = "Results: \n"

    cur.execute("SELECT doc_name from doc_list where doc_name LIKE '%"+ doctor_name+"%';")
    rows = cur.fetchall()
    # conn.close()
    conn2 = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")
    cur2 = conn2.cursor()


    if len(rows) ==1:
        cur2.execute("INSERT INTO Appointments values(' "+doctor_name+" ',' "+date1+" ');")
        # cur2.execute("INSERT INTO Appointments values('Zxcvb','2018-06-30');")
        response = "Successfully booked an appointment with Dr. " +doctor_name+ " on " +date1

        # if d1>d2:
        #     cur2.execute("INSERT INTO Appointments values('Qwerty','2018-05-30');")
        #     # cur2.execute("INSERT INTO Appointments values(' "+doctor_name+" ',' "+date1+" ');")
        #     response = "Successfully booked an appointment with Dr. " +doctor_name+ " on " +date1
        # else:
        #     response = "Invalid date to book an appointment"

    elif len(rows)>1:
        for row in rows:
            response = response + row[0] + "\n"
    elif len(rows)==0:
        response = "Sorry! I couldn't find any doctor with that name."

    conn2.commit()
    conn2.close()
    conn.close()
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
