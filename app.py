import json
from flask import Flask, request, make_response, jsonify
import psycopg2
import difflib

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

    outputContexts = ""

    if action == 'isValidDoctor':
        res, outputContexts = is_valid_doctor(req)
        # req['queryResult']['outputContexts']['name'] = outputContexts

    elif action == 'SelectDoctor':
        res = select_doctor(req)

    elif action == 'Check_Sickness.Check_Sickness-yes':
        res = display_doctor_from_dept(req)

    elif action == 'Check_Sickness.Check_Sickness-yes.Check_Sickness-yes-custom':
        res = select_doctor_dept(req)

    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)

    # req['queryResult']['outputContexts']['name'] = outputContexts
    return make_response(jsonify({'fulfillmentText': res, 'outputContexts':req['queryResult']['outputContexts']}))
                        #,'outputContexts': [{'name': "chooseDoctor"}]


def display_doctor_from_dept(req):

    dept_name = req['queryResult']['outputContexts'][0]['parameters']['disease_name']
    disease_name = req['queryResult']['outputContexts'][0]['parameters']['disease_name.original']

    conn = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    doc_cur = conn.cursor()

    cur.execute("SELECT department_id from department where department_name = '"+ dept_name+"';")
    rows = cur.fetchall()

    for row in rows:
        dept_id = str(row[0])

    response = "Found these doctors that specialize in treating your sickness\n"

    doc_cur.execute("SELECT doc_name from doc_list where department_id = '"+dept_id+"' ; ")
    rows = doc_cur.fetchall()

    doctor_number=0                     #For the user to select from list of doctors

    if len(rows) == 0:
        return ":-("

    for row in rows:
        doctor_number+=1
        response = response + str(doctor_number)  + ". Dr." + str(row[0]) + " of " + dept_name + ",\n"

    response += "\n Please Choose by Number"

    conn.close()
    return response


def select_doctor(req):

    conn = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    select_cur = conn.cursor()

    doctor_name = req['queryResult']['outputContexts'][0]['parameters']['doctor_name']
    doctor_name = ''.join(doctor_name)
    doctor_name = doctor_name.strip().title()
    doctor_name = doctor_name.replace("Dr. ","")
    doctor_name = doctor_name.replace("dr ","")
    doctor_name = doctor_name.replace("Dr ","")

    doctor_number = int(req['queryResult']['parameters']['number-integer'])
    # doctor_number = doctor_number - 1

    select_cur.execute("SELECT doc_name, doc_id from doc_list where doc_name LIKE '%"+ doctor_name+"%';")
    rows = select_cur.fetchall()

    i = 0
    for row in rows:

        if i  == doctor_number - 1:
            doctor_name = str(row[0])
            doctor_id = str(row[1])
            break
        i += 1


    datetime = req['queryResult']['outputContexts'][0]['parameters']['date-time']['date_time']
    datetime = ''.join(datetime)
    date_of_app = datetime[:10]
    time_of_app = datetime[11:19]

    cur.execute("SELECT * from Appointments where App_Date ='"+date_of_app+"' AND App_Time = '"+time_of_app+"' AND Doctor_ID='"+doctor_id+"' ")
    if_doc_busy_rows = cur.fetchall()

    if len(if_doc_busy_rows) < 1:
        cur.execute("INSERT INTO Appointments(Doctor_ID, App_Date, App_Time) values(' "+doctor_id+" ',' "+date_of_app+" ','"+time_of_app+"');")
        response = "Successfully booked with "+doctor_name+" on "+date_of_app+" at "+time_of_app
    else:
        response = "I'm sorry. "+doctor_name+" seems to be busy at that time."

    conn.commit()
    conn.close()
    return response


def select_doctor_dept(req):

    conn = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")
    select_cur = conn.cursor()
    cur = conn.cursor()
    cur_check_appointment = conn.cursor()
    cur_insert_appointment = conn.cursor()

    doctor_number = int(req['queryResult']['parameters']['number-integer'])
    dept_name = req['queryResult']['outputContexts'][0]['parameters']['disease_name']

    cur.execute("SELECT department_id from department where department_name = '"+ dept_name+"';")
    rows = cur.fetchall()

    for row in rows:
        dept_id = str(row[0])


    select_cur.execute("SELECT doc_name,doc_id from doc_list where department_id = '"+dept_id+"' ; ")
    rows = select_cur.fetchall()

    i = 0
    for row in rows:
        if i  == doctor_number - 1:
            doctor_name = str(row[0])
            doctor_id = str(row[1])
            break
        i += 1


    datetime = req['queryResult']['parameters']['date-time']['date_time']
    datetime = ''.join(datetime)
    date_of_app = datetime[:10]
    time_of_app = datetime[11:19]

    cur_check_appointment.execute("SELECT * from Appointments where App_Date ='"+date_of_app+"' AND App_Time = '"+time_of_app+"' AND Doctor_ID='"+doctor_id+"' ")
    if_doc_busy_rows = cur_check_appointment.fetchall()

    if len(if_doc_busy_rows) < 1:
        cur_insert_appointment.execute("INSERT INTO Appointments(Doctor_ID, App_Date, App_Time) values(' "+doctor_id+" ',' "+date_of_app+" ','"+time_of_app+"');")
        response = "Successfully booked with "+doctor_name+" on "+date_of_app+" at "+time_of_app
    else:
        response = "I'm sorry. Dr. "+doctor_name+" seems to be busy at that time."

    conn.commit()
    conn.close()
    return response


def is_valid_doctor(req):

    outputContexts=""
    # outputContexts = req['queryResult']['outputContexts']['name']
    datetime = req['queryResult']['parameters']['date-time']['date_time']
    datetime = ''.join(datetime)
    date_of_app = datetime[:10]
    time_of_app = datetime[11:19]

    doctor_name = req['queryResult']['parameters']['doctor_name']
    doctor_name = ''.join(doctor_name)
    doctor_name = doctor_name.strip().title()
    doctor_name = doctor_name.replace("Dr. ","")
    doctor_name = doctor_name.replace("dr ","")
    doctor_name = doctor_name.replace("Dr ","")

    conn = psycopg2.connect(database = "db0ntdu7buk51i", user = "tibwcqkplwckqf", password = "9cfed858b1d9206afb594c1c5cfacc5952b2fc21d440501daa3af5efd694313c", host = "ec2-107-20-249-68.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    dept_cursor = conn.cursor()
    match_cursor = conn.cursor()

    response = "Found these results: \nWhich Doctor where you looking for?\n"

    cur.execute("SELECT doc_name, department_id, doc_id from doc_list where doc_name LIKE '%"+ doctor_name+"%';")
    rows = cur.fetchall()

    for row in rows:
        doctor_name = str(row[0])
        doctor_id = str(row[2])

    response = "Invalid Choice!"
    cur2 = conn.cursor()

    if len(rows) ==1:
        cur.execute("SELECT * from Appointments where App_Date ='"+date_of_app+"' AND App_Time = '"+time_of_app+"' AND Doctor_ID='"+doctor_id+"' ")
        if_doc_busy_rows = cur.fetchall()

        if len(if_doc_busy_rows) < 1:
            cur.execute("INSERT INTO Appointments(Doctor_ID, App_Date, App_Time) values(' "+doctor_id+" ',' "+date_of_app+" ','"+time_of_app+"');")
            response = "Successfully booked with "+doctor_name+" on "+date_of_app+" at "+time_of_app
        else:
            response = "I'm sorry. "+doctor_name+" seems to be busy at that time."

    elif len(rows)>1:
        doctor_number=0                     #For the user to select from list of doctors

        for row in rows:
            doctor_number+=1
            dept_cursor.execute( "SELECT department_name from department where department_id = '"+str(row[1])+"' ;" )
            dept_list = dept_cursor.fetchall()
            response = response + str(doctor_number)  + ". Dr." + str(row[0]) + " of " + dept_list[0][0] + ",\n"

        response += "\n Please Choose by Number"
        outputContexts = "chooseDoctor"

    elif len(rows)==0:
        response = "Sorry! I couldn't find any doctor with that name."
        all_doctors = []

        match_cursor.execute("SELECT doc_name from doc_list;")
        all_rows = match_cursor.fetchall()
        for row in all_rows:
            all_doctors.append(row[0])

        best_match=sorted(a, key=lambda x: difflib.SequenceMatcher(None, x, b).ratio(), reverse=True)

        response = response + "\nBest match for that name is Dr. " + best_match[0]

    conn.commit()
    conn.close()
    return response,outputContexts


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
