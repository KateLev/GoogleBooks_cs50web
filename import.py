import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL")) 
db = scoped_session(sessionmaker(bind=engine))  # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate


f = open("books.csv") #open csv file
reader = csv.reader(f) #reader is a new object where each row is the list of strings 

for row in reader: # To remove the first string in csv file
	row.remove
	break

for isbn_python, title, author, year in reader: # loop gives each column a name
	db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn_python, :title, :author, :year)",
	{"isbn_python":isbn_python, "title":title, "author":author, "year":year })
	db.commit()
	