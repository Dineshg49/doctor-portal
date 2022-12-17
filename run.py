
from flask import Flask, request, jsonify , session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required,login_user

import uuid
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.dirname(__file__)) + '/uploads/'

db = SQLAlchemy(app)

class Receptionist(db.Model):
    __tablename__ = 'receptionists'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    record = db.Column(db.String(50), nullable=False)

db.create_all()


@app.route('/login', methods=['POST'])
def login():
    Usertype = request.json['Usertype']
    username = request.json['username']
    password = request.json['password']
    if Usertype == 'receptionist':
        user = Receptionist.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials!'})
        session['username'] = username
        session['usertype'] = 'receptionist'
        return jsonify({'message': 'Logged in successfully!'})
    elif Usertype == 'doctor':
        user = Doctor.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials!'})
        session['username'] = username
        session['usertype'] = 'doctor'
        return jsonify({'message': 'Logged in successfully!'})
    elif Usertype == 'patient':
        user = Patient.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials!'})
        session['username'] = username
        session['usertype'] = 'patient'
        return jsonify({'message': 'Logged in successfully!'})
    return jsonify({'message': 'Wrong Usertype!'})


# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    Usertype = request.form['Usertype']
    username = request.form['username']
    password = request.form['password']
    if Usertype == 'receptionist':
        receptionist = Receptionist(username=username, password=generate_password_hash(password))
        db.session.add(receptionist)
        db.session.commit()
        return jsonify({'message': 'Registration successfull'})
    elif Usertype == 'doctor':
        doctor = Doctor(username=username, password=generate_password_hash(password))
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'message': 'Registration successfull'})
    elif Usertype == 'patient':
        patient = Patient(username=username, password=generate_password_hash(password))
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Registration successfull'})
    return jsonify({'message': 'Wrong Usertype!'})


@app.route('/doctor/bookAppointment', methods=['POST'])
def doctor_book_appointment(): 

     
    patient_id = request.form['patient_id']
    appointment_date = request.form['appointment_date']
    doctor = Doctor.query.get(username = session['username']).first()

    appointment = Appointment.query.filter_by(doctor_id=doctor.id, date=appointment_date,patient_id=patient_id).first()
    if appointment is not None:
        return jsonify({"error": "Appointment already booked"}), 400
    
    
    new_appointment = Appointment(doctor_id=doctor.id,
                                patient_id=patient_id,
                                appointment_date=appointment_date)
    db.session.add(new_appointment)
    db.session.commit()
 
    return jsonify({'message': 'Appointment has been created successfully.'}), 201



@app.route("/patient/bookAppointment", methods=["POST"])
def pateint_book_appointment():
     
    doctor_id = request.form['doctor_id']
    appointment_date = request.form['appointment_date']
    patient = Patient.query.get(username = session['username']).first()

    appointment = Appointment.query.filter_by(doctor_id=doctor_id, date=appointment_date,patient_id=patient.id).first()
    if appointment is not None:
        return jsonify({"error": "Appointment already booked"}), 400
    
    
    new_appointment = Appointment(doctor_id=doctor_id,
                                patient_id=patient.id,
                                appointment_date=appointment_date)
    db.session.add(new_appointment)
    db.session.commit()
 
    return jsonify({'message': 'Appointment has been created successfully.'}), 201


@app.route('/receptionist/bookAppointment', methods=['POST'])
def book_appointment():
     
    doctor_id = request.form['doctor_id']
    appointment_date = request.form['appointment_date']
    patient_id = request.form['patient_id']


    appointment = Appointment.query.filter_by(doctor_id=doctor_id, date=appointment_date,patient_id=patient_id).first()
    if appointment is not None:
        return jsonify({"error": "Appointment already booked"}), 400
    
    
    new_appointment = Appointment(doctor_id=doctor_id,
                                patient_id=patient_id,
                                appointment_date=appointment_date)
    db.session.add(new_appointment)
    db.session.commit()
 
    return jsonify({'message': 'Appointment has been created successfully.'}), 201

@app.route('/patient/uploadMedicalRecord', methods=['POST'])
def upload_medical_record():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file found"}), 400
    

     
    doctor_id = request.form['doctor_id']
    appointment_date = request.form['appointment_date']
    patient = Patient.query.get(username = session['username']).first()


    appointment = Appointment.query.filter_by(doctor_id=doctor_id, date=appointment_date,patient_id=patient.id).first()
    if appointment is None:
        return jsonify({"error": "First Create an Appointment to Upload Record"}), 400    

    filename = str(uuid.uuid4())
    filename += '.pdf'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    new_record = MedicalRecord(appointment_id=appointment.id,record=filename)

    db.session.add(new_record)
    db.session.commit()
 
    return jsonify({'message': 'Record has been uploaded successfully'}), 201



@app.route('/doctor/viewMedicalRecord', methods=['POST'])
def view_patient_medical_record():
     
    patient_id = request.form['patient_id']
    appointment_date = request.form['appointment_date']
    doctor = Doctor.query.get(username = session['username']).first()

    appointment = Appointment.query.filter_by(doctor_id=doctor.id, date=appointment_date,patient_id=patient_id).first()
    if appointment is None:
        return jsonify({"error": "No Appointment booked for this patient at provided date"}), 400
    
    medicalRecord = MedicalRecord.query.filter_by(appointment_id=appointment.id).first()

    if medicalRecord is None :
        return jsonify({"error": "No Record Found"}), 400
    
    filename = medicalRecord.record

    return jsonify(filename)        

if __name__ == '__main__':
    app.run(debug=True)