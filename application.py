import os
import requests
import flask_login
import json

from flask import Flask, session, render_template, request, jsonify
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
		return render_template("index.html")
	return render_template("login.html")

	
@app.route("/book")
def book():
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "tZLOtICC4yMSdeSIbKV0lQ", "isbns": "9780804139298"})
	return res.json()
	
@app.route("/login", methods=["POST", "GET"])
def login():
	username = request.form.get("username")
	print('username', username, '\n\n' )
	password = request.form.get("password")	
	print('password', password, '\n\n' )
	id = db.execute("SELECT id FROM users WHERE name=:name and pass=:password", {"name":username, "password":password}).fetchone() 
	
	if id: #if it exist		
		session["user_id"] = id[0]
		print("session['user_id']", session["user_id"]  )
		return render_template("index.html", username = username)
	else:
		return render_template("login.html", error = "Wrong username or password")
	

	
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
		return render_template("index.html", username = username)
		
	else:
		return render_template("reg.html", error = "The name is already exist")

@app.route("/logout", methods=["POST", "GET"])		
def logout():
	print(session.sid)
	session.clear()	
	return render_template("login.html", error = "You are sucessfully logged out")

@app.route("/search", methods=["POST"])	
def search():
	searchFor = request.form.get("Search")
	checker = 0
	searchFor = searchFor.strip()
	
	#return empty index page
	if (searchFor == ""):
		return render_template("index.html", checker = checker)	
	
	#search for coincidence	
	isbn_coincidence = db.execute(f"SELECT isbn, title, author from books WHERE isbn LIKE '%{searchFor}%'").fetchall()
	titles_coincidence = db.execute(f"SELECT isbn, title, author from books WHERE title LIKE '%{searchFor}%'").fetchall()
	author_coincidence = db.execute(f"SELECT isbn, title, author from books WHERE author LIKE '%{searchFor}%'").fetchall()
	
	# Way to see how query is look like	
	#	print(str((f"SELECT isbn, title, author from books WHERE isbn LIKE '%{searchFor}%'")))
	
	coincidence = []
	coincidence.extend(isbn_coincidence)
	coincidence.extend(titles_coincidence)
	coincidence.extend(author_coincidence)
	
	#return empty index page
	if coincidence == []:
		checker = 1
		return render_template("index.html", checker = checker)	
	
	checker = 2
	
	print("searchFor", '+', searchFor, '+')
	print("type", type(coincidence))
	print("searchFor", type(searchFor))
	
	lenght = len(coincidence)
	return render_template("index.html", checker = checker, coincidence = coincidence, lenght = lenght)

@app.route("/books/<string:book_isbn>", methods=["GET"])
def more(book_isbn):

	#split to remove tab symbols, [0] because after split method book_isbn became a list
	book_isbn = book_isbn.split()[0]
	
	# https://www.goodreads.com/api/index taken from api
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "tZLOtICC4yMSdeSIbKV0lQ", "isbns": book_isbn})
	
	#	res.json() is a dictionary
	data = res.json()
	
	# ways to access the data. We can return many books in request, so I need to access 0 element of an array
	
	#print ("""data["books"]""", data["books"])
	#print ("""data["books"][0]""", data["books"][0])
	#print ("""data["books"][0][average_rating]""", data["books"][0]['average_rating'])
	
	avg_rating = data["books"][0]['average_rating']
	ratings_count = data["books"][0]['ratings_count']
	book_info = db.execute(f"SELECT title, author, year from books WHERE isbn=:book_isbn", {"book_isbn":book_isbn}).fetchone()
	book_title = book_info["title"]
	book_author = book_info["author"]
	book_year = book_info["year"]
	return render_template ("book.html", avg_rating = avg_rating, \
	ratings_count = ratings_count, book_title = book_title, book_author = book_author, \
	book_isbn = book_isbn, book_year = book_year)

@app.route("/api/<string:book_isbn>", methods=["GET"])
def book_json(book_isbn):
	book_info = db.execute(f"SELECT title, author, year from books WHERE isbn=:book_isbn", {"book_isbn":book_isbn}).fetchone()
	#print(book_info)
	#print(json.dumps({'author':book_info[1],'title':book_info[0], 'year':book_info[2]}, sort_keys=True, indent=4))
	#print(json.dumps({'4': 5, '6': 7}, sort_keys=True, indent=4))
	if (book_info is None):
		return render_template("error.html", error_number = "404")
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "tZLOtICC4yMSdeSIbKV0lQ", "isbns": book_isbn})
	data = res.json()
	
	return jsonify(title =  str(book_info[0]).strip(), author = str(book_info[1]).strip(),  year = book_info[2], isbn = book_isbn, average_score = data["books"][0]['average_rating'], ratings_count = data["books"][0]['ratings_count'])
	
	