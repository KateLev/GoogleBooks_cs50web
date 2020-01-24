import os
import requests
import flask_login

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__) # Instantiate a new web application called `app`, with `__name__` representing the current file

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
current_user_id = 0

@app.route("/", methods=["GET", "POST"])
def index():		
	# check if user is currently logged in
	if 'username' in session:
		username = session['username']
		return render_template("index.html", username = username)
	return render_template("login.html")

	
@app.route("/book")
def book():
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "tZLOtICC4yMSdeSIbKV0lQ", "isbns": "9780804139298"})
	return res.json()
	
@app.route("/login", methods=["POST", "GET"])
def login():
	return "You are not logged in"
	
@app.route("/reg", methods=["POST", "GET"])
def reg():	
	return render_template("reg.html")
	
@app.route("/reg_success", methods=["POST"])
def reg_form():
	username = request.form.get("username")
	password = request.form.get("password")
	
	#check for existanse in table users. If there is no such name, add to users table
	check_name = db.execute("SELECT name FROM users WHERE name = :username", {"username":username}).rowcount 
		
	if check_name == 0:
		db.execute("INSERT INTO users (name, pass) VALUES (:name, :pass)", {"name":username, "pass":password} )
		db.commit()
		
		#А если будет без fetchone, то sqlacademy возвращает объект ResultProxy 
		current_user_id = db.execute("SELECT id from users WHERE name=:name", {"name":username}).fetchone() 		
		session["user_id"] = current_user_id[0]			
		session['username'] = username		
		return render_template("index.html")
		
	else:
		return "The name is already exist"

@app.route("/logout", methods=["POST", "GET"])		
def logout():
	print(session.sid)
	session['username'] = None
	print (session['username'])
	return render_template("index.html", username = session['username'])
	

