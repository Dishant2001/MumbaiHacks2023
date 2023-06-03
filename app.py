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
from mail import mail
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

@app.route("/logout",methods=['GET'])
def logout():
    session.clear()
    return json.dumps({"mssg":200})

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
                session['uid'] = row.uid
                session['role'] = row.role
                    
                    # print("logged in")
                print(session['uid'])

                user_data = {
                        "uid": row.username,
                        "role": row.role,
                        "username": row.username,
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
    

@app.route('/getloc',methods=['GET'])
def location():
    import random
    lat = random.randint(0,100)
    lon = random.randint(0,100)
    return jsonify({'user_longitude':lon,'user_latitude':lat,"mec_longitude":lon,'mec_latitude':lat})

@app.route('/location',methods=['GET','POST'])
def loc():
    return render_template('user/track-mechanics.html')

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
             INSERT into mechanicshop(shop_id,crn) VALUES(:uid,:crn)
            """
            db.session.execute(query2,{
                "uid":uid,
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
             INSERT into mechanics(mechanic_id, shop_id, experience, specialization, rating, services) VALUES(:uid,:shop_id, :experience, :specialization, :rating, :services)
            """
        db.session.execute(query2,{
            "uid":uid,"shop_id":session.get('username'), "experience":experience, "specialization":specialization, "rating":rating, "services":services
        })

        db.session.commit()

        mail.send_mail('mad1.21f1006594@gmail.com','lajihgnqebnnhlso', uid, uid, password, name)

        # redirect('/dashboard')
        return json.dumps({"mssg":200})
    

@app.route('/request',methods=['GET','POST'])
def req():
    if request.method=='POST' and session.get('uid') is not None and session.get('role') in ['4',4]:
        data = request.get_json()
        uid = session.get('uid')
        car_pic = data['car_pic']
        car_name = data['car_name']
        car_brand = data['car_brand']
        req = data['request']
        user_latitude = data['user_latitude']
        user_longitude = data['user_longitude']
        timestamp = datetime.now()
        status = 0
        query = """
                INSERT INTO requests (uid, car_pic, car_name, car_brand, request, user_latitude,user_longitude,timestamp_,status)
                VALUES (:uid, :car_pic, :car_name, :car_brand, :request, :user_latitude,:user_longitude,:timestamp_,:status)
            """
        db.session.execute(query, {
                "uid":uid, "car_pic":car_pic, "car_name":car_name, "car_brand":car_brand, "request":req, "user_latitude":user_latitude,"user_longitude":user_longitude,"timestamp_":timestamp,"status":status
            })
        db.session.commit()

        return json.dumps({"mssg":200})
    

@app.route('/getNearestRequests',methods=['GET','POST'])
def getNearestRequest():
    if request.method=="POST" and session.get("uid") is not None and session.get("role") in [6,'6']:
        data = request.get_json()
        mech_lat = data['latitude']
        mech_long = data['longitude']
        query = """
        SELECT *, 
            (
                6371 * 
                acos(
                    cos(radians(:given_latitude)) * 
                    cos(radians(user_latitude)) * 
                    cos(radians(user_longitude) - radians(:given_longitude)) + 
                    sin(radians(:given_latitude)) * 
                    sin(radians(user_latitude))
                )
            ) AS distance
        FROM requests
        ORDER BY distance;

        """
        results = db.session.execute(query,{
            "given_latitude":mech_lat,
            "given_longitude":mech_long,
        })

        req_list = []
        
        for req in results:
            d = {}
            d["customer"] = req.uid
            d["car_pic"] = req.car_pic
            d["car_name"] = req.car_name
            d["car_brand"] = req.car_brand
            d["request"] = req.request
            d["request_id"] = req.request_id
            d['user_latitude'] = str(req.user_latitude)
            d['user_longitude'] = str(req.user_longitude)
            d["timestamp"] = req.timestamp_.strftime("%Y-%m-%d %H:%M:%S")
            req_list.append(d)

        db.session.commit()

        return json.dumps({"messg":200,"requests":req_list})
    
@app.route('/acceptRequest',methods=['GET','POST'])
def acceptRequest():
    if request.method=="POST" and session.get("uid") is not None and session.get("role") in ['6',6]:
        data = request.get_json()
        mid = session.get('uid')
        req_id = data['request_id']
        mech_lat = data['latitude']
        mech_long = data['longitude']
        query = """
        UPDATE requests SET status = 1, mech_latitude = :mech_lat, mech_longitude = :mech_long, mid = :mid WHERE request_id = :req_id;
        """

        db.session.execute(query,{
            "mech_lat":mech_lat,
            "mech_long":mech_long,
            "mid":mid,
            "req_id":req_id
        })

        db.session.commit()

        return json.dumps({"mssg":200})


            




if __name__=="__main__":
    app.run(debug=True, port=8000)