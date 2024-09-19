import os
import datetime
import flask
from flask import Flask, render_template, request, jsonify, send_from_directory
from langchain_core.messages import SystemMessage, HumanMessage
import sqlite3

from src import initialize_llm, parse_results
from config import *


# Start Flask app
app = Flask(__name__)

# Initialize LLM
agent = initialize_llm(USER_NAME, HOST, k=K, max_tokens=MAX_TOKENS, temp=T)
chat_history = []


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/msg", methods=["POST"])
def chat():
    # Retrieve message
    msg = request.form["msg"]
    print("Received: {}".format(msg))
    
    # Register new message in user's chat history
    append_to_history(msg, 'user')
    
    # Add new message to chat history
    global chat_history
    chat_history.append(HumanMessage(content=msg))
    if len(chat_history) > CHAT_BUFFER: chat_history = chat_history[-CHAT_BUFFER:]
    
    # Invoke chat agent to answer query
    result=agent.invoke({"messages": chat_history})
    #result = {"messages": chat_history + [SystemMessage(content="Hello World!")]}
    print("Response: {}".format(result))
    
    # Return agent's response and update chat history accordingly
    chat_history, response = parse_results(result)
    if len(chat_history) > CHAT_BUFFER: chat_history = chat_history[-CHAT_BUFFER:]
    
    # Register new message in user's chat history
    append_to_history(response, 'bot')
    
    return response

def append_to_history(text, source):
    file_path = os.path.join(CHAT_HISTORY_FOLDER, USER_NAME.lower() + '.txt')
    t = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'a') as f:
        f.write("[{}] {}: {}\n\n".format(t, source, text))
    

def retrieve_appointment(slot_id):
    # Open connection to DB
    db = sqlite3.connect('assets/database/medassist.db')
    cur = db.cursor()
    
    # Prepare query to retrieve time slot information
    query = """
            SELECT doctor, time_slot, patient
            FROM appointments
            WHERE id = ?
        """
    
    # Execute query and fetch result
    result = cur.execute(query, (slot_id,))
    return result.fetchone()


def set_appointment(patient, slot_id):
    # Open connection to DB
    db = sqlite3.connect('assets/database/medassist.db')
    cur = db.cursor()
    
    # Prepare query to retrieve time slot information
    query = """
            UPDATE appointments
            SET patient = ?
            WHERE id = ?
        """
    
    # Execute query
    cur.execute(query, (patient, slot_id,))
    db.commit()

@app.route("/history", methods=["GET"])
def history():
    return send_from_directory(CHAT_HISTORY_FOLDER, USER_NAME.lower() + '.txt')

@app.route("/res", methods=["GET"])
def reserve():
    # Retrieve slot id
    slot_id = int(request.args.get('id'))
    print("Slot id: {}".format(slot_id))
    
    # Retrieve time slot details
    row = retrieve_appointment(slot_id)
    
    # If no results were found, raise error
    if row is None:
        return flask.abort(404)
    
    # Parse result
    doctor, time_slot, patient = row
    slot_status = "reserved" if patient is not None else "available"
    
    # Check that patient is authorized to access the required information
    if slot_status == "reserved" and patient.lower() != USER_NAME.lower():
        return flask.abort(401)
    
    return render_template('reservation.html', slot_id=slot_id, doctor=doctor, time_slot=time_slot, slot_status=slot_status)

@app.route("/setReservation", methods=["POST"])
def setReservation():
    # Retrieve request information
    target_slot_id = int(request.form['slot_id'])
    
    print("Requested reservation for time slot {}, from user {}".format(target_slot_id, USER_NAME))
    
    # Retrieve time slot information
    row = retrieve_appointment(target_slot_id)
    
    # If no results were found, return error
    if row is None:
        return jsonify({"response": "Unable to process request.", "slot_status": "reserved"})
    print("Slot details: {}".format(row))
    
    # Parse result
    doctor, time_slot, patient = row
    slot_status = "reserved" if patient is not None else "available"
    
    # Check if user is authorized to manage reservation
    if slot_status == "reserved" and USER_NAME.lower() != patient.lower():
        return jsonify({"response": "Unable to process request.", "slot_status": "reserved"})
    
    # If slot not already reserved, make reservation
    if slot_status == "available":
        set_appointment(USER_NAME, target_slot_id)
    
    return jsonify({"response": "Reservation successful", "slot_status": "reserved"})


@app.route("/cancelReservation", methods=["POST"])
def cancelReservation():
    # Retrieve request information
    target_slot_id = int(request.form['slot_id'])
    
    print("Reservation cancel requested for time slot {}, from user {}".format(target_slot_id, USER_NAME))
    
    # Retrieve time slot information
    row = retrieve_appointment(target_slot_id)
    
    # If no results were found, return error
    if row is None:
        return jsonify({"response": "Unable to process request.", "slot_status": "reserved"})
    print("Slot details: {}".format(row))
    
    # Parse result
    doctor, time_slot, patient = row
    slot_status = "reserved" if patient is not None else "available"
    
    # Check if user is authorized to manage reservation
    if slot_status == "reserved" and USER_NAME.lower() != patient.lower():
        return jsonify({"response": "Unable to process request.", "slot_status": "reserved"})
        
    # Cancel reservation, if necessary
    if slot_status == "reserved":
        set_appointment(None, target_slot_id)
    
    return jsonify({"response": "Cancellation successful", "slot_status": "available"})


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)
