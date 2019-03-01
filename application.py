import os
''' 
Prevent the users from making account with invalid username and password and username, disable the submit button if the user 
handle various cases
'''

from flask import Flask, session,render_template,request
import requests
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# setting the session
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.config['SECRET_KEY']='super secret key'

username=""

# set the database
engine = create_engine("postgres://wxwjtpitggoati:8dfb1487bafbda798870df37a4691bf46afd7162e0d8f3932e7ae20854cd4f89@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d50618rt42i32c")
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
'''
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
'''

@app.route("/")
def index():
	if username!="" :
	    return render_template('home.html',name=session[username])
	else:
	    return render_template('home.html',name="")

# this is the login page
@app.route("/login")
def login():
	return render_template('login.html')

# this woul be the first page seen by the user when he is loged in
@app.route("/welcome",methods=["POST"])
def welcome():
	name=request.form.get("name")
	username=request.form.get("username")
	password=request.form.get("password")
	# check if the correct user logged in or not
	password_from_db=db.execute("SELECT password FROM users_record where username =:username", {"username": username}).fetchone()
	# if we donot find any user then prompt the page saying that wrong credentials entered ,and give the option of forget password
	if password_from_db is None:# means there is no user
		return render_template('register.html')
	if password_from_db[0]!=password:
		return render_template('login.html',message="U have forgot your password or username")
	# make entry in the session
	session['username']=username
	return render_template('welcome.html',name=name)

@app.route("/logout")
def logout():
	# make the user log out from the 
	# remove the username from the session if it is there
    session.pop('username', None)
    return render_template('home.html')

# this is the registration page
@app.route("/register")
def register():
	# if u are creating a new account then logout from current session
	logout()
	# what is happening is home page is being and then register.html is being rendered
	return render_template('register.html',register="")

@app.route("/create_account",methods=["POST"])
def create_account():
	# if u are creating a new account then logout from current session
	logout()
	name=request.form.get("name")
	username=request.form.get("username")
	password=request.form.get("password")
	# check if the user name already exist then donot allow account making
	user_conflict=db.execute("SELECT * FROM users_record where username =:username", {"username": username}).fetchone()
	# if no conflict occur create the account and if some database error occur say that accordingly
	if user_conflict is None:
		db.execute("INSERT INTO users_record (name,username,password) VALUES (:name,:username,:password)",{"name":name,"username":username,"password":password})
		db.commit()
		# creating a session here , that is when user has made a new account
		session['username']=username
		return render_template('welcome.html',name=name+" Your account has been created")
	else:
		return render_template('register.html',message="Please try with different user name")

@app.route("/search")
def search():
	return render_template('search_query.html')

@app.route("/fetch_data",methods=["POST"])
def fetch_data():
	# what if user didnot apply any filter
	x=request.form.get("ISBN")
	y=request.form.get("author")
	z=request.form.get("title")
	isbn=author=title=""
	if len(x)>0 and len(y)>0 and len(z)>0:
		# if user has used all the valid filters
		isbn=x
		isbn='%'+isbn+'%'
		author=y
		author='%'+author+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title and author like :author" , {"isbn": isbn,"title":title,"author":author})

	elif len(y)==0 and len(x)>=1 and len(z)>=1:
		# if isbn and title are valid
		isbn=x
		isbn='%'+isbn+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title " , {"isbn": isbn,"title":title})
	elif len(z)==0 and len(x)>=1 and len(y)>=1:
		# if we have valid isbn and author only
		isbn=x
		isbn='%'+isbn+'%'
		author=y
		author='%'+author+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and author like :author" , {"isbn": isbn,"author":author})
	
	elif len(x)==0 and len(y)>0 and len(z)>0:
		# we have valid author and title only
		author=y
		author='%'+author+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where title like :title and author like :author" , {"title":title,"author":author})
	else:
		return '<h1>Enter some valid filters, you didnot apply any of them </h1>'
	
	# let us try for small search ,search only isbn
	# make cases when two filter are empty or one is empty
	#booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title and author like :author" , {"isbn": isbn,"title":title,"author":author}).fetchall()
	db.commit()
	list_book=[]
	for b in booklist:
		list_book.append(b)
	return render_template('book_info.html',booklist=list_book)
	#return str(list_book)
	# too much work for api donot do it hear booklist=get_info(list_book)
	#print(booklist)

	

# We donot require it @app.route("/api_request",methods=["POST"])# only the pages can ask for the details
def get_info(booklist):
	'''
	data_dict=res.json()
	print(data_dict['books'][0])# this gives u access to the dictionary now give third parameter as isbn or id or rating count or etc
	'''
	# get the average score for each book
	# what we should do is make a page for search about the books and then get the information from database into a list and that list passed to this function and then we append more data to it about ,average rating and then at last rendering the page and giving it the data to display in beautiful table format
	final_list=[]
	for b in booklist:
		b=list(b)
		res=requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"44ZCyFojgwqbYPzQ2vfw","isbns":b[0]})
		#b.append(res.json()['books'][0]['average_score'])
		if res != None:
			rating=res.json()['books'][0]['average_rating']
			#rating=str(rating)
			b=b.append(rating)
			final_list.append(b)
		else :# in case we have no ratng for a book
			final_list.append(b)
	return final_list
