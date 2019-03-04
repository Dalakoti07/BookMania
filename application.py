import os
''' 
Prevent the users from making account with invalid username and password and username, disable the submit button if the user 
handle various cases
'''

from flask import Flask, session,redirect,url_for,render_template,request,jsonify
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

def helper(isbn):
	isbn='%'+isbn+'%'
	query=db.execute("SELECT * FROM book_record where id like :isbn" , {"isbn": isbn}).fetchall()
	db.commit()
	book=query[0]
	book=list(book)
	res=requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"44ZCyFojgwqbYPzQ2vfw","isbns":book[0]})
	rating=res.json()['books'][0]['average_rating']
	work_reviews_count=res.json()['books'][0]['reviews_count']
	book.append(rating)
	book.append(work_reviews_count)
	return book

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
@app.route("/welcome",methods=["POST","GET"])
def welcome():
	name=request.form.get("name")
	username=request.form.get("username")
	password=request.form.get("password")
	password=hash(password)
	# check if the correct user logged in or not
	password_from_db=db.execute("SELECT password FROM users_record where username =:username", {"username": username}).fetchone()
	# if we donot find any user then prompt the page saying that wrong credentials entered ,and give the option of forget password
	if password_from_db is None:# means there is no user
		return redirect('/register')
	if password_from_db[0]!=password:
		return redirect(url_for('/login'))
		#return render_template('login2.html',message="U have forgot your password or username")
	# make entry in the session
	session['username']=username
	return redirect(url_for('success'))
	#return render_template('welcome2.html')

@app.route("/success")
def success():
	return render_template('success.html')

# incomplete
@app.route('/post/<string:isbn>',methods=['POST'])
def post(isbn):
	if 'username' in session:
		review_text=request.form.get("comments")
		username=session['username']
		id_from_db=db.execute("SELECT id FROM users_record where username =:username", {"username": username}).fetchone()
		id_user=id_from_db[0]
		db.execute("INSERT INTO review_record (user_id,book_id,review_text) VALUES (:uid,:bid,:rtext)",{"uid":id_user,"bid":isbn,"rtext":review_text})
		db.commit()
		return redirect('/book/isbn')
	else:
		return '<h1> Please register</h1>'

@app.route("/logout")
def logout():
	# make the user log out from the 
	# remove the username from the session if it is there
    session.pop('username', None)
    return redirect('home.html')

# this is the registration page
@app.route("/register")
def register():
	# if u are creating a new account then logout from current session
	logout()
	# what is happening is home page is being and then register.html is being rendered
	return render_template('register.html',register="")

@app.route("/create_account",methods=["POST","GET"])
def create_account():
	# if u are creating a new account then logout from current session
	logout()
	name=request.form.get("name")
	username=request.form.get("username")
	password=request.form.get("password")
	password=hash(password)
	# check if the user name already exist then donot allow account making
	user_conflict=db.execute("SELECT * FROM users_record where username =:username", {"username": username}).fetchone()
	# if no conflict occur create the account and if some database error occur say that accordingly
	if user_conflict is None:
		db.execute("INSERT INTO users_record (name,username,password) VALUES (:name,:username,:password)",{"name":name,"username":username,"password":password})
		db.commit()
		# creating a session here , that is when user has made a new account
		session['username']=username
		return redirect('/welcome')
	else:
		return render_template('register.html',message="Please try with different user name")

@app.route("/search")
def search():
	return render_template('search.html')

@app.route("/fetchdata",methods=["POST","GET"])
def fetchdata():
	# what if user didnot apply any filter
	x=request.form.get("ISBN")
	y=request.form.get("author")
	z=request.form.get("title")
	isbn=author=title=""
	if x!=None and y!=None and z!=None:
		# if user has used all the valid filters
		isbn=x
		isbn='%'+isbn+'%'
		author=y
		author='%'+author+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title and author like :author" , {"isbn": isbn,"title":title,"author":author})

	elif y==None and x!=None and z!=None:
		# if isbn and title are valid
		isbn=x
		isbn='%'+isbn+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title " , {"isbn": isbn,"title":title})
	elif z==None and x!=None and y!=None:
		# if we have valid isbn and author only
		isbn=x
		isbn='%'+isbn+'%'
		author=y
		author='%'+author+'%'
		booklist=db.execute("SELECT * FROM book_record where id like :isbn and author like :author" , {"isbn": isbn,"author":author})
	
	elif x==None and y!=None and z!=None:
		# we have valid author and title only
		author=y
		author='%'+author+'%'
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where title like :title and author like :author" , {"title":title,"author":author})
	elif x==None and y==None and z!=None:
		title=z
		title='%'+title+'%'
		booklist=db.execute("SELECT * FROM book_record where title like :title " , {"title":title})
	elif y==None and z==None and x!=None:
		isbn=x
		isbn='%'+isbn+'%'
		booklist=db.execute("SELECT * FROM book_record where isbn like :isbn" , {"title":isbn})
	elif x==None and z==None and y!=None:
		author=y
		author='%'+author+'%'
		booklist=db.execute("SELECT * FROM book_record where author like :author" , {"author":author})
	else:
		return '<h1>Enter some valid filters, you didnot apply any of them </h1>'
	
	# let us try for small search ,search only isbn
	# make cases when two filter are empty or one is empty
	#booklist=db.execute("SELECT * FROM book_record where id like :isbn and title like :title and author like :author" , {"isbn": isbn,"title":title,"author":author}).fetchall()
	db.commit()
	list_book=[]
	for b in booklist:
		list_book.append(b)
	#return redirect(url_for('.do_foo', messages=messages))
	return render_template('booklist.html',booklist=list_book)
	#return str(list_book)
	# too much work for api donot do it hear booklist=get_info(list_book)
	#print(booklist)

@app.route('/book/<string:isbn>')
def book_data(isbn):
	book=helper(isbn)
	return render_template('details.html',details=book)

@app.route('/api/<string:isbn>')
def apis(isbn):
	book=helper(isbn)
	# id title autjor year
	return jsonify({
		"title":book[1],
		"author":book[2],
		"year":book[3],
		"isbn":book[0],
		"review_count":book[5],
		"average_score":book[4]
	})


# We donot require it @app.route("/api_request",methods=["POST"])# only the pages can ask for the details
'''def get_info(booklist):
	
	data_dict=res.json()
	print(data_dict['books'][0])# this gives u access to the dictionary now give third parameter as isbn or id or rating count or etc
	
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
'''