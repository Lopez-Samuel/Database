import hashlib
import datetime
#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='testing',
                       db='DBP3',
                       charset='latin1',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    md5password = hashlib.md5(password).hexdigest()

    # cursor used to send queries
    cursor = conn.cursor()

    # executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, md5password))

    # stores the results in a variable
    data = cursor.fetchone()

    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    if (data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        session['logged_in'] = True
        return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    md5password = hashlib.md5(password).hexdigest()

    # print type(username)
    # print type(md5password)
    # print type(firstname)
    # print type(lastname)
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
        cursor.execute(ins, (username, md5password, firstname, lastname))
        conn.commit()
        cursor.close()
        successful = "registeration is complete, log in below to start pricosha"
        return render_template('index.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    username=session['username']
    cursor=conn.cursor()
    name=request.form['content name']
    filepath=request.form['filepath']
    query='INSERT INTO content (`username`, `file_path`, `content_name`, `public`) VALUES (%s, %s, %s,1)'
    cursor.execute(query, (username, filepath, name))
    conn.commit()
    cursor.close()
    return render_template('home.html')

@app.route('/home', methods = ['GET', 'POST'])
def home():
    username = session['username']
    time = datetime.datetime.now()
    cursor = conn.cursor()
    query = 'SELECT id, timest, content_name, username, count(*) as num FROM content NATURAL JOIN likes GROUP BY id'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, content = data) #used to say user=username


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

# @app.route('/add_Friend', methods = ['GET', 'POST'])
# def add_Friend():
#     username = session['username']
#     friendGroup = request.form['FriendGroup']
#     firstName = request.form['First Name']
#     lastName = request.form['Last Name']
#     cursor.conn.cursor()
#     query = 'SELECT username FROM Person WHERE first name  = %s AND last name = %s'
#     cursor.execute(query,(firstName, lastName))
#     cursor.close()
#     queryCheck = 'COUNT * FROM Member HAVING username = %s AND group_name = %s AND username_creator = %s '
#     cursor.execute(queryCheck,(query,FriendGroup, username))
#     error = None
#     if (queryCheck != 1 ):
#         error ='More than one user with name ' firstName ' ' lastName 'exists in friend group ' friendGroup'
#         return render_template('home.html', error = error)
#     else
#         addFriend = 'SELECT username FROM '

# @app.route('/addFriendgroup', methods = ['POST'])
# def addFriendgroup():
#     username = session['username']
#     friendGroup = request.form['Friendgroup']
    

@app.route('/addComment', methods=['GET', 'POST'])
def addComment():
    username=session['username']
    cursor=conn.cursor()
    comment=request.form['comment']
    query="INSERT INTO comment('id', 'username', 'comment') VALUES (%i, %s, %s,)"
    cursor.execute(query, (id, username, comment))
    conn.commit()
    cursor.close()
    return render_template('home.html')

@app.route('/like', methods=['GET', 'POST'])
def like():
    username=session['username']
    cursor=conn.cursor()
    query="INSERT INTO likes('id', 'username',) VALUES (%i, %s,)"
    cursor.execute(query, (id, username))
    conn.commit()
    cursor.close()
    return render_template('home.html')
@app.route('/add_Friend', methods = ['GET', 'POST'])
def add_Friend():
    username = session['username']
    friendGroup = request.form['FriendGroup']
    firstName = request.form['First Name']
    lastName = request.form['Last Name']
    description = request.form['Description']
    cursor = conn.cursor()
    query = 'SELECT username FROM Person WHERE first name  = %s AND last name = %s'
    cursor.execute(query,(firstName, lastName))
    cursor.close()
    queryCheck = 'COUNT * FROM Member HAVING username = %s AND group_name = %s AND username_creator = %s '
    cursor.execute(queryCheck,(query, friendGroup, username))
    error = None
    if (queryCheck != 1 ):
        error ='More than one user with name ' firstName ' ' lastName 'exists in friend group ' friendGroup'
        return redirect(url_for('home'), error= error)
    else
        cursor = conn.cursor()
        addFriendQuery= 'INSERT INTO `Member` (`username`, `group_name`, `username_creator`) VALUES (%s,%s,%s)'
        cursor.execute(addFriendQuery, (friendGroup,query,username))
        cursor.close()
        return redirect(url_for('home'))


@app.route('/addFriendgroup', methods = ['POST'])
def addFriendgroup():
    username = session['username']
    friendGroup = request.form['Friendgroup']
    friend = request.form['Friend']
    query = 'SELECT '
    

@app.route('/addComment/<int:line_id>', methods=['GET', 'POST'])
def addComment(line_id):
    id=line_id
    username=session['username']
    cursor=conn.cursor()
    comment=request.form['comment']
    query='INSERT INTO comment(`id`, `username`, `comment_text`) VALUES (%s, %s, %s)'
    cursor.execute(query, (id, username, comment))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/like/<int:line_id>', methods=['GET', 'POST'])
def like(line_id):
    id=line_id
    username=session['username']
    cursor=conn.cursor()
    query='INSERT INTO likes(`username`, `id`) VALUES (%s, %s)'
    cursor.execute(query, (username, id))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


app.secret_key = 'x53467Dbahb2!23'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
