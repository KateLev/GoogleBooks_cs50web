# Project 1

File import.py is a separate file that copy all entries from book.csv to database.

Folder static/css/style.css is responsible for style.

File templates/layout.html is a base for other webpages

The project has three tables: 
	books (isbn, author, avgRating, title, year)
	Rating (user_id, review, isbn, rating)
	users (id, name, pass)
	
To connect with database:
set DATABASE_URL=postgres://raodzgeefvysrp:75f54487f22672844059c173c2688e1fb8c00723de8967ae3b7fd472ffcca3bb@ec2-107-21-235-87.compute-1.amazonaws.com:5432/d386i5ratos175


Requerments:
1. Registration. Is available via Registration button on the main page. If user's name is already exist, it returns an error message on the reg.html web page. 
In application.py reg and reg_form functions are responsible for functionality, template reg.html.
2. Login. Is available via Login button on the main page. If user's name and password are not suitable, error pop-ups on login page.
3. Logout. Is available via Logout button on the main page.
4. Import. I created import.py file to import data to sql table.
5. Search. After you logged in, you can search for title, ISBN, or author name. "Search" function is responsible for this.
6. Book Page. Is available after clicking "See more" after search.
7. Review Submission. Is available on book.html page. If review was submitted earlier, I made error page with 33 code.
8. Goodreads Review Data is available on book web page.
9. API Access realised via book_json function.


