import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
import requests
from werkzeug.exceptions import abort

logged_user = None

def checkSignedIn():
    input = {
        "input":{
            "user" : str(logged_user)
        }
    }
    print(input)

    r = requests.post('http://localhost:8181/v1/data/authentication/loginAllow',json = input)
    result = r.json()
    return result["result"]

def canCreate():
    input = {
        "input":{
            "user" : logged_user
        }
    }

    r = requests.post('http://localhost:8181/v1/data/authentication/loginAllow',json = input)
    result = r.json()
    return result["result"]


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


def retrieveUsers():
	conn = get_db_connection()
	conn.execute("SELECT username, password, permissions FROM users")
	users = conn.fetchall()
	conn.close()
	return users


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    if checkSignedIn() == True:
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM posts').fetchall()
        conn.close()
        return render_template('index.html', posts=posts)
    else:
        flash('Kindly LogIn to access this content')
        return redirect(url_for('loginUser'))
    


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    # if canCreate() == False:
    #     flash("You don't have the permission to create blog")
    #     return redirect(url_for('loginUser'))

    return render_template('create.html')

@app.route('/register', methods=('GET', 'POST'))
def registerUser():
    if request.method == 'POST':
        print("entered")
        username = request.form['username']
        password = request.form['password']
        permissions = request.form['permissions']
        print(username, password, permissions)
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username,password,permissions) VALUES (?,?,?)", (username,password,permissions))
        conn.commit()
        conn.close()
        return redirect(url_for('loginUser'))
  
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def loginUser():
    global logged_user
    if request.method == 'POST':
        # print("entered")
        username = request.form['username']
        password = request.form['password']
        # return username
        # print("Hello", username, password)
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? and password = ?',(username,password)).fetchone()
        conn.close()
        # print("user " , dict(user))
        if user is None:
            flash('User does not exist, Kindly register!')
            return redirect(url_for('registerUser'))
        else :
            tempUser = dict(user)
            permissions = tempUser['permissions'].split()
            tempUser['permissions'] = permissions
            logged_user = tempUser
            print(logged_user)
            flash('Welcome "{}"'.format(logged_user['username']))
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    global logged_user
    if(checkSignedIn()) :
        logged_user = None
        flash('Successfully Logged Out')

    else:
        flash('Already Logged Out')
    return redirect(url_for('loginUser'))

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
