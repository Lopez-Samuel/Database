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
    return redirect(url_for('home'))

@app.route('/home', methods = ['GET', 'POST'])
def home():
    username = session['username']
    time = datetime.datetime.now()
    cursor = conn.cursor()
    fg = 'SELECT group_name, username, description FROM friendgroup WHERE username = %s'
    cursor.execute(fg, (username))
    friendGroup = cursor.fetchall()
    query = 'SELECT COUNT(likes.username) as num, content.id, timest, content_name, content.username, file_path FROM content LEFT JOIN likes ON content.id= likes.id GROUP BY content.id'
    cursor.execute(query)
    data = cursor.fetchall()
    query3='SELECT tag.id, username_tagger, content_name FROM tag JOIN content ON tag.id=content.id WHERE tag.username_taggee= %s AND tag.status= "0"'
    cursor.execute(query3, (username))
    pending_tags=cursor.fetchall()
    cursor.close()
    return render_template('home.html', username = username, content = data, friendGroup = friendGroup, pending_tags = pending_tags)

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

@app.route('/add_Friend/<group_name>', methods = ['GET', 'POST'])
def add_Friend(group_name):
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    username = session['username']
    cursor = conn.cursor()
    query2 = 'SELECT COUNT(*) as num FROM Person WHERE first_name = %s AND last_name = %s'
    cursor.execute(query2,(firstName, lastName))
    count= cursor.fetchone()
    error = None
    if(count['num'] == 1):
        query3 = 'SELECT username FROM Person WHERE first_name = %s AND last_name = %s'
        cursor.execute(query3,(firstName, lastName))
        friendun = cursor.fetchone()
        addFriendQuery= 'INSERT INTO `Member` (`username`, `group_name`, `username_creator`) VALUES (%s,%s,%s)'
        cursor.execute(addFriendQuery,(friendun['username'],group_name,username))
        conn.commit()
        query = 'SELECT Member.username, first_name, last_name FROM Member JOIN Person ON Member.username= Person.username WHERE group_name = %s'
        cursor.execute(query, (group_name))
        allMembers2 = cursor.fetchall()
        cursor.close()
        return render_template('viewFriendGroup.html', data= allMembers2, group_name= group_name)
    elif(count['num'] != 1):
        query = 'SELECT Member.username, first_name, last_name FROM Member JOIN Person ON Member.username= Person.username WHERE group_name = %s'
        cursor.execute(query, (group_name))
        allMembers = cursor.fetchall()
        cursor.close()
        error ='More than one user with name ' + firstName  + ' ' + lastName + ' exists in PriCoSha'
        return render_template('viewFriendGroup.html', group_name = group_name, data=allMembers, error = error)

@app.route('/addFriendGroup', methods = ['POST'])
def addFriendgroup():
    username = session['username']
    friendGroup = request.form['Friend Group']
    friend = request.form['Friend']
    description = request.form['Description']
    cursor = conn.cursor()
    query = 'INSERT INTO `FriendGroup` (`group_name`, `username`, `description`) VALUES (%s, %s, %s)'
    cursor.execute(query, (friendGroup, username, description))
    conn.commit()
    query2 = 'INSERT INTO `Member` (`username`, `group_name`, `username_creator`) VALUES (%s, %s, %s)'
    cursor.execute(query2, (friend, friendGroup, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
    
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
    

@app.route('/viewFriendGroup/<group_name>', methods = ['GET', 'POST'])
def viewFriendGroup(group_name):
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT Member.username, first_name, last_name FROM Member JOIN Person ON Member.username= Person.username WHERE group_name = %s'
    cursor.execute(query, (group_name))
    data = cursor.fetchall()
    return render_template('viewFriendGroup.html', data = data, group_name = group_name)

@app.route('/tag/<int:data_id>', methods=['GET', 'POST'])
def tag(data_id):
    id = data_id
    username = session['username']
    taggee = request.form['Tag']
    cursor = conn.cursor()
    query = 'INSERT INTO `Tag` (`id`, `username_tagger`, `username_taggee`, `status`) VALUES (%s, %s, %s, 0)'
    cursor.execute(query, (id,username,taggee))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
    
@app.route('/view/<int:line_id>', methods=['GET', 'POST'])
def view(line_id):
    id = line_id
    username = session['username']
    cursor = conn.cursor()
    query = "SELECT count(*) as num FROM likes WHERE id=%s GROUP BY id"
    cursor.execute(query, (id))
    number_of_likes = cursor.fetchone()
    query = "SELECT id, file_path, username, timest, content_name FROM content WHERE id=%s"
    cursor.execute(query, (id))
    line = cursor.fetchone()
    query = "SELECT comment_text FROM comment WHERE id=%s"
    cursor.execute(query, (id))
    comments = cursor.fetchall()
    query="SELECT first_name, last_name FROM Person LEFT OUTER JOIN tag ON tag.username_taggee=Person.username WHERE tag.status='1' AND tag.id=%s"
    cursor.execute(query, (id))
    tags=cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('view.html', username=username, id = line_id, data = line, number_of_likes = number_of_likes, comments = comments, tags = tags)

@app.route('/approve/<un>/<un_tagger>/<int:line_id>', methods=['GET', 'POST'])
def approve(un, un_tagger, line_id):
    cursor=conn.cursor()
    query="UPDATE tag set status='1' WHERE tag.username_tagger=%s AND tag.Username_taggee=%s AND tag.id=%s"
    cursor.execute(query, (un_tagger, un, line_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

@app.route('/ignore/<un>/<un_tagger>/<int:line_id>', methods=['GET', 'POST'])
def ignore(un, un_tagger, line_id):
    cursor=conn.cursor()
    query="UPDATE tag  set status='0' WHERE tag.username_tagger=%s AND tag.Username_taggee=%s AND tag.id=%s"
    cursor.execute(query, (un_tagger, un, line_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('home')) 

@app.route('/deny/<un>/<un_tagger>/<int:line_id>', methods=['GET', 'POST'])
def delete(un, un_tagger, line_id):
    cursor=conn.cursor()
    query="DELETE FROM tag WHERE tag.username_tagger=%s AND tag.Username_taggee=%s AND tag.id=%s"
    cursor.execute(query, (un_tagger, un, line_id))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))

app.secret_key = 'x53467Dbahb2!23'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
