from flask import Flask, render_template, redirect, session, request, jsonify
import json
from dotenv.main import load_dotenv
from flask_session import Session
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_cors import CORS
import random
import string
import hashlib
import mail
from datetime import datetime, timedelta
from utility import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app)
load_dotenv()
app.secret_key = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_PATH']               #'mysql://root:@localhost/bhumika_portfolio'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)


# class Users(db.Model):
#     uid = db.Column(db.Integer, primary_key=True)
#     role = db.Column(db.Integer,nullable=False)
#     date = db.Column(db.String(20), nullable=False)
#     name = db.Column(db.String(120), nullable=False)
#     phone = db.Column(db.String(12), nullable=False)
#     country = db.Column(db.String(120), nullable=False)
#     state = db.Column(db.String(120), nullable=False)
#     address = db.Column(db.String(255), nullable=False)
#     city = db.Column(db.String(120), nullable=False)



salt_length = 6

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('user/index.html')

@app.route('/request',methods=['GET','POST'])
def requestMechanics():
    return render_template('user/request.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST' and session.get("uid")==None:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        print("username: ",username)
        print("password: ",password)
        query = """
        SELECT * from users WHERE uid = :uid
        """
        row = db.session.execute(query,{'uid':username}).first()
        if row is not None:
            salt = row.salt
            print("salt: ",salt)
            
            hex_dig = hashPassword(password,salt)
            print(hex_dig)
            if hex_dig==row.password:
                session['uid'] = row.username
                session['role'] = row.role
                    
                    # print("logged in")
                print(session['uid'])

                user_data = {
                        "uid": row.username,
                        "role": row.role,
                        "username": row.name,
                        "phone": row.phone,
                        "address":row.address
                }

                #     return json.dumps({
                # "username":user.username,
                # "role":user.role,
                # "date":user.date.strftime("%Y-%m-%d"),
                # "name":user.name,
                # "phone":user.phone,
                # "email":user.email,
                # "country":user.country,
                # "state":user.state,
                # "address":user.address,
                # "city":user.city
                # })
                return jsonify(user_data)
                    
                
    else:
        return jsonify({'mssg':'already logged in or incorrect password','name':None})
    

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST' and session.get('uid') is None:
        data = request.get_json()
        role = data['role']
        
        salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=salt_length))
        
        if role == 4:  #customer role
            uid = data['username']
            name = data['name']
            phone = data['phone']
            address = data['address']
            password = data['password']
            hex_dig = hashPassword(password,salt)
            # query = """
            #  INSERT into users() VALUES({},{},{},{},{},{},{})
            # """.format(uid, name, phone, address, role, hex_dig, salt)
            # db.session.execute(query)
            query = """
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """
            db.session.execute(query, {
                'uid': uid,
                'name': name,
                'phone': phone,
                'address': address,
                'role': role,
                'password': hex_dig,
                'salt': salt
            })

            db.session.commit()
            return json.dumps({"mssg":200})
        if role == 5: #mechanic shop role
            uid = data['username']
            name = data['name']
            phone = data['phone']
            address = data['address']
            crn = data['crn']
            password = data['password']
            hex_dig = hashPassword(password,salt)
            query = """
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """
            db.session.execute(query, {
                'uid': uid,
                'name': name,
                'phone': phone,
                'address': address,
                'role': role,
                'password': hex_dig,
                'salt': salt
            })

            query2 = """
             INSERT into mechanicshop(shop_id,shop_name, location, phone_number,crn) VALUES(:uid,:name,:address,:phone,:crn)
            """
            db.session.execute(query2,{
                "uid":uid,
                "name":name,
                "address":address,
                "phone":phone,
                "crn":crn
            })

            db.session.commit()

            return json.dumps({"mssg":200})
        

@app.route('/addmechanic',methods=['GET','POST'])
def addmechanic():
    if request.method=='POST' and session.get('uid') is not None and session.get('role') in [5,'5']:
        data = request.get_json()
        uid = data['username']
        name = data['name']
        phone = data['phone']
        address = data['address']
        experience = data['experience']
        specialization = data['specialization']
        services = data['services']
        rating = 75
        password = uid
        salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=salt_length))
        hex_dig = hashPassword(password,salt)
        role = 6 #mechanic
        query = """
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """
        db.session.execute(query, {
                'uid': uid,
                'name': name,
                'phone': phone,
                'address': address,
                'role': role,
                'password': hex_dig,
                'salt': salt
            })

        query2 = """
             INSERT into mechanics(mechanic_id, mechanic_name, mechanic_phone, shop_id, experience, specialization, rating, services) VALUES(:uid, :name, :phone, :shop_id, :experience, :specialization, :rating, :services)
            """
        db.session.execute(query2,{
            "uid":uid, "name":name, "phone":phone, "shop_id":session.get('username'), "experience":experience, "specialization":specialization, "rating":rating, "services":services
        })

        db.session.commit()

        mail.send_mail('mad1.21f1006594@gmail.com','lajihgnqebnnhlso', uid, uid, password, name)

        # redirect('/dashboard')
        return json.dumps({"mssg":200})

            




if __name__=="__main__":
    app.run(debug=True)