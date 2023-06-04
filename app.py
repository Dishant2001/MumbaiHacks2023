from flask import Flask, render_template, redirect, session, request, jsonify
import json
from dotenv.main import load_dotenv
from flask_session import Session
from sqlalchemy import text
import os
from flask_sqlalchemy import SQLAlchemy
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
    return render_template('user/index.html', request=request)

@app.route('/new-request',methods=['GET','POST'])
def requestMechanics():
    if request.method=="GET" and session.get("uid") is not None:
        return render_template('user/request.html')
    else:
        return render_template('login.html')

@app.route("/logout",methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/view-mechanics', methods=['GET','POST'])
def viewMechanical():
    return render_template('mechanics/view-mechanics.html', request=request)

@app.route('/add-mechanics', methods=['GET','POST'])
def addMechanical():
    return render_template('mechanics/add-mechanical.html', request=request)

@app.route('/mechanics-profile', methods=['GET','POST'])
def mechanicProfile():
    uid = session.get('uid')
    query = text(f"SELECT * FROM users WHERE uid='{uid}';")
    row = db.session.execute(query).first()
    query = text(f"SELECT * FROM mechanics WHERE mechanic_id='{uid}';")
    row1 = db.session.execute(query).first()
    query = text(f"SELECT username FROM users WHERE uid='{row1[1]}'")
    shop = db.session.execute(query).first()
    return render_template('mechanics_profile.html',  user=row, mech=row1, shop=shop)

@app.route('/view-request', methods=['GET','POST'])
def viewRequest():
    return render_template('mechanics/view-request.html', request=request)

@app.route('/track-mechanics/<id>', methods=['GET','POST'])
def trackMechanic(id):
    session['request_id'] = id
    return render_template('user/track-mechanics.html', request=request)

@app.route('/getRequestData',methods=["GET"])
def getReqData():
    req_id = session.get("request_id")
    query = """
        SELECT * FROM requests WHERE request_id = :req_id
        """
    row = db.session.execute(query,{"req_id":req_id}).fetchone()
    d={}
    d['user_latitude'] = float(row.user_latitude)
    d['user_longitude'] = float(row.user_longitude)

    return json.dumps({"data":d})

@app.route('/track-users/<id>', methods=['GET','POST'])
def trackUser(id):
    session["request_id"] = id
    return render_template('user/track-users.html', request=request)


@app.route('/user-login', methods=['GET'])
def authentication():
    return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST' and session.get("uid")==None:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        print("username: ",username)
        print("password: ",password)
        query = text("SELECT * from users WHERE uid=:uid")
        row = db.session.execute(query,{'uid':username}).first()
        if row is not None:
            salt = row.salt
            print("salt: ",salt)
            
            hex_dig = hashPassword(password,salt)
            print(hex_dig)
            if hex_dig==row.password:
                session['uid'] = row.uid
                session['role'] = row.role
                session['name'] = row.username
                    
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
    return render_template('user/track-mechanics.html', request=request)

@app.route('/location-user',methods=['GET','POST'])
def loc_user():
    return render_template('user/track-users.html', request=request)



@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST' and session.get('uid') is None:
        data = request.get_json()
        print(data)
        role = int(data['role'])
        
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
            query = text(
                """
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """
            )
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
            query = text(
                """
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """
            )
            db.session.execute(query, {
                'uid': uid,
                'name': name,
                'phone': phone,
                'address': address,
                'role': role,
                'password': hex_dig,
                'salt': salt
            })

            query2 = text(
                """
             INSERT into mechanicshop(shop_id,crn) VALUES(:uid,:crn)
            """
            )
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
       
        query = text("""
                INSERT INTO users (uid, username, phone, address, role, password, salt)
                VALUES (:uid, :name, :phone, :address, :role, :password, :salt)
            """)
        db.session.execute(query, {
                'uid': uid,
                'name': name,
                'phone': phone,
                'address': address,
                'role': role,
                'password': hex_dig,
                'salt': salt
            })

        query2 = text("""
            INSERT into mechanics(mechanic_id, shop_id, experience, specialization, rating, services) VALUES(:uid,:shop_id, :experience, :specialization, :rating, :services)
            """)
        db.session.execute(query2,{
            "uid":uid,"shop_id":session.get('uid'), "experience":experience, "specialization":specialization, "rating":rating, "services":services
        })

        db.session.commit()
        print('hel,')
        mail.send_mail('mad1.21f1006594@gmail.com','lajihgnqebnnhlso', uid, uid, password, name)

        # redirect('/dashboard')
        return json.dumps({"mssg":200})
        
    else:
        return render_template('mechanics/add-mechanical.html')
    

@app.route('/request',methods=['GET','POST'])
def req():
    if request.method=='POST' and session.get('uid') is not None and session.get('role') in ['4',4]:
        data = request.get_json()
        uid = session.get('uid')
        car_pic = data['car_pic']
        car_name = data['car_brand']
        car_brand = data['car_brand']
        req = data['fault']
        user_latitude = data['user_latitude']
        user_longitude = data['user_longitude']
        timestamp = datetime.now()
        status = 0
        query = text(
            """
                INSERT INTO requests (uid, car_pic, car_name, car_brand, request, user_latitude,user_longitude,timestamp_,status)
                VALUES (:uid, :car_pic, :car_name, :car_brand, :request, :user_latitude,:user_longitude,:timestamp_,:status)
            """
        )
        db.session.execute(query, {
                "uid":uid, "car_pic":car_pic, "car_name":car_name, "car_brand":car_brand, "request":req, "user_latitude":user_latitude,"user_longitude":user_longitude,"timestamp_":timestamp,"status":status
            })
        db.session.commit()
        print(data)
        return json.dumps({"mssg":200})
    else:
        return render_template('user/request.html', request=request)
    
# @app.route('/fetchloc',methods=['GET'])
# def locationfetch():
#     r_id = session.get('')
    
@app.route('/update',methods=['GET','POST'])
def updreq():
    if request.method=='POST' and session.get('uid') is not None and session.get('role') in ['4',4]:
        data = request.get_json()
        uid = session.get('uid')
        car_pic = data['car_pic']
        car_name = data['car_brand']
        car_brand = data['car_brand']
        req = data['fault']
        user_latitude = data['user_latitude']
        user_longitude = data['user_longitude']
        timestamp = datetime.now()
        status = 0
        query = text(
            """
                INSERT INTO requests (uid, car_pic, car_name, car_brand, request, user_latitude,user_longitude,timestamp_,status)
                VALUES (:uid, :car_pic, :car_name, :car_brand, :request, :user_latitude,:user_longitude,:timestamp_,:status)
            """
        )
        db.session.execute(query, {
                "uid":uid, "car_pic":car_pic, "car_name":car_name, "car_brand":car_brand, "request":req, "user_latitude":user_latitude,"user_longitude":user_longitude,"timestamp_":timestamp,"status":status
            })
        db.session.commit()
        print(data)
        return json.dumps({"mssg":200})
    else:
        return render_template('user/request.html', request=request)
    

@app.route('/getNearestRequests',methods=['GET','POST'])
def getNearestRequest():
    if request.method=="POST" and session.get("uid") is not None and session.get("role") in [6,'6']:
        print("Inside getrequests")
        data = request.get_json()
        mech_lat = data['latitude']
        mech_long = data['longitude']
        query = text(
            """
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
        FROM requests WHERE status = 0
        ORDER BY distance;

        """
        )
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
    if request.method=="POST" and session.get("uid") is not None and session.get("role") in ['6',6] and session.get("req_id") is None:
        data = request.get_json()
        mid = session.get('uid')
        req_id = data['request_id']
        mech_lat = data['latitude']
        mech_long = data['longitude']
        query = text(
            """
        UPDATE requests SET status = 1, mech_latitude = :mech_lat, mech_longitude = :mech_long, mid = :mid WHERE request_id = :req_id;
        """
        )

        db.session.execute(query,{
            "mech_lat":mech_lat,
            "mech_long":mech_long,
            "mid":mid,
            "req_id":req_id
        })

        db.session.commit()

        session['req_id'] = req_id
        session['status'] = 1

        return json.dumps({"mssg":200})
    
@app.route('/getShopNearestRequests',methods = ["GET","POST"])
def getShopNearestRequests():
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [5,'5']:
        # data = request.get_json()
        # mech_lat = data['latitude']
        # mech_long = data['longitude']
        query = text(
            """
        SELECT address FROM users WHERE uid = :uid
        """
        )
        result = db.session.execute(query,{"uid":session.get("uid")}).fetchone()
        lat = ''
        long = ''
        if result:
            address = result.address
            lat = float(address.split('+')[0])
            long = float(address.split('+')[1])

        query2 = text(
            """
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
        FROM requests WHERE status NOT IN (1,2)
        ORDER BY distance;

        """
        )
        results = db.session.execute(query2,{
            "given_latitude":lat,
            "given_longitude":long,
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
    

@app.route('/getRequests',methods = ["GET","POST"])
def getRequests():
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [6,'6']:
        # data = request.get_json()
        # mech_lat = data['latitude']
        # mech_long = data['longitude']
        query = text(
            """
        SELECT * FROM requests WHERE mid = :mid
        """
        )
        results = db.session.execute(query,{"mid":session.get("uid")})

        

        req_list = []
        
        for req in results:
            d = {}
            
            d["car_name"] = req.car_name
            d["request_id"] = req.request_id
            d["timestamp"] = req.timestamp_.strftime("%Y-%m-%d %H:%M:%S")
            d["status"] = req.status
            req_list.append(d)

        return json.dumps({"messg":200,"requests":req_list})
    
@app.route('/getUserRequests',methods = ["GET","POST"])
def getUserRequests():
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [4,'4']:
        # data = request.get_json()
        # mech_lat = data['latitude']
        # mech_long = data['longitude']
        query = text(
            """
        SELECT * FROM requests WHERE uid = :uid
        """
        )
        results = db.session.execute(query,{"uid":session.get("uid")})

        

        req_list = []
        
        for req in results:
            d = {}
            
            d["car_name"] = req.car_name
            d["request_id"] = req.request_id
            d['status'] = req.status
            d["timestamp"] = req.timestamp_.strftime("%Y-%m-%d %H:%M:%S")
            req_list.append(d)

        return json.dumps({"messg":200,"requests":req_list})
    

@app.route('/assignMechanic',methods=['GET','POST'])
def assignMechanic():
    if request.method=='POST' and session.get('uid') is not None and session.get("role") in ['5',5]:
        data = request.get_json()
        mid = data['mid']
        req_id = data['request_id']
        query = text(
            """
        UPDATE requests SET mid = :mid, status = 1 WHERE request_id = :req_id 
        """
        )
        db.session.execute(query,{"req_id":req_id,"mid":mid})
        db.session.commit()
        return json.dumps({"mssg":200})
    

@app.route('/getMechanics',methods=['GET','POST'])
def getMechanics():
    print('Entered outside')
    if request.method=='GET' and session.get('uid') is not None and session.get("role") in ['5',5]:
        print("Entered inside")
        query = text(
            """
        SELECT * from mechanics WHERE shop_id=:shop_id 
        """
        )
        results = db.session.execute(query,{"shop_id":session.get("uid")})
        mech_list = []
        for req in results:
            d={}
            d['mech_id'] = req.mechanic_id
            d['experience'] = req.experience
            d['specialization'] = req.specialization
            d['rating'] = req.rating
            d['services'] = req.services
            mech_list.append(d)
        return json.dumps({"mssg":200,"mechanics":mech_list})
    
@app.route('/assignedRequests',methods=['GET',"POST"])
def assignedRequests():
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [6,'6']:
        query = text(
            """
        SELECT * from requests WHERE mid=:mid AND mech_latitude IS NULL
        """
        )
        results = db.session.execute(query,{"mid":session.get("uid")})
        
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
            session['req_id'] = req.request_id
            session['status'] = 1
            req_list.append(d)

        db.session.commit()

        return json.dumps({"messg":200,"requests":req_list})
    
@app.route('/getMechLocation/<id>',methods=['GET','POST'])
def getMechLocation(id):
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [4,'4']:
        query = text(
            """
        SELECT * from requests WHERE request_id = :req_id
        """
        )
        results = db.session.execute(query,{"req_id":id}).fetchone()
        if results:
            latitude = results.mech_latitude
            longitude = results.mech_longitude
            return json.dumps({"latitude":latitude,"longitude":longitude})
        
@app.route('/myRequest',methods=['GET','POST'])
def myRequest():
    if request.method=="GET" and session.get("uid") is not None and session.get("role") in [4,'4']:
        query = text(
            """
        SELECT * from requests WHERE request_id = :req_id
        """
        )
        
        results = db.session.execute(query,{"req_id":session.get("request_id")}).fetchone()
        print(results)
        if results:
            user_latitude = float(results.user_latitude)
            user_longitude = float(results.user_longitude)
            mech_latitude = float(results.mech_latitude)
            mech_longitude = float(results.mech_longitude)
            return json.dumps({"user_latitude":user_latitude,"user_longitude":user_longitude,"mech_latitude":mech_latitude,"mech_longitude":mech_longitude})
    
@app.route('/updateMechanicLocation',methods=['GET','POST'])
def updateloc():
    if request.method=='POST' and session.get("uid") is not None and session.get("role") in ['6',6]:
        data = request.get_json()
        mech_lat = data['latitude']
        mech_long = data['longitude']
        req_id = session.get("request_id")
        print(req_id)
        query = text(
            """
        UPDATE requests SET mech_latitude = :mech_lat, mech_longitude = :mech_long WHERE request_id = :req_id
        """
        )
        db.session.execute(query,{"req_id":req_id,"mech_lat":mech_lat,"mech_long":mech_long})
        db.session.commit()
        if session.get("status") is None:
            return json.dumps({"status":2})
        return json.dumps({"mssg":200})
        
@app.route('/completeRequest',methods=['GET','POST'])
def completeRequest():
    if request.method=="POST" and session.get("uid") is not None and session.get("role") in ['6',6]:
        mid = session.get('uid')
        req_id = session.get("request_id")
        query = text(
            """
        UPDATE requests SET status = 2 WHERE request_id = :req_id;
        """
        )

        db.session.execute(query,{
            "req_id":req_id
        })

        db.session.commit()

        session.pop("request_id")
        session.pop("status")

        return json.dumps({"mssg":200})
    
        
@app.route('/customer-profile',methods=['GET','POST'])
def customer_profile():
    uid = session.get('uid')
    query = text(f"SELECT * FROM users WHERE uid='{uid}';")
    row = db.session.execute(query).first()
    print(row)
    return render_template('customer_profile.html', user=row)

@app.route('/shop-profile',methods=['GET','POST'])
def shop_proflie():
    uid = session.get('uid')
    query = text(f"SELECT * FROM users WHERE uid='{uid}';")
    row = db.session.execute(query).first()
    query = text(f"SELECT * FROM mechanicshop WHERE shop_id='{uid}';")
    row1 = db.session.execute(query).first()
    print(row, row1)
    return render_template('shop_profile.html',user=row, shop=row1,)





            




if __name__=="__main__":
    app.run(debug=True, port=8000)