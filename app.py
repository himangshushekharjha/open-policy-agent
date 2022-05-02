import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
import requests
from werkzeug.exceptions import abort
from functools import wraps
import json 

logged_user = None
opa_url = 'http://localhost:8181/v1/data/authentication/'

def checkSignedIn():
    input = {
        "input":{
            "user" : str(logged_user)
        }
    }
    # print(input)
    r = requests.post(opa_url + 'isUserLoggedIn',json = input)
    result = r.json()
    # print("########RESULT##########",result)
    return result["result"]

def approveJira(input):
    global logged_user
    input['pullRequestIDs'] = []
    conn = get_db_connection()
    pullRequestIDs = conn.execute('SELECT id FROM pullRequests').fetchall()
    conn.close()
    for pullRequestID in pullRequestIDs:
        input['pullRequestIDs'].append(list(pullRequestID)[0])
    
    input['user'] = {}
    input['user'] = logged_user
    res = {}
    res['input'] = {}
    res['input'] = input
    # print("#################Input#######",json.dumps(res,indent=4))
    r = requests.post(opa_url + 'approveJira',json = res)
    result = r.json()
    print('sentttttt', res)
    print("RRRRRRRRRRR",result)
    return result["result"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        global logged_user
        # print("########logged_user#######",logged_user)

        if checkSignedIn() == True: 
            return f(*args, **kws)   
        else:
            flash('Kindly LogIn to access this content')
            return redirect(url_for('loginUser'))
    return decorated_function


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

def get_jira(jira_id):
    conn = get_db_connection()
    jira = conn.execute('SELECT * FROM jiras WHERE id = ?',
                        (jira_id,)).fetchone()
    conn.close()
    if jira is None:
        abort(404)
    return jira


def retrieveUsers():
	conn = get_db_connection()
	conn.execute("SELECT username, password, permissions FROM users")
	users = conn.fetchall()
	conn.close()
	return users


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)
    
@app.route('/jiras')
@login_required
def jiras():
    
    conn = get_db_connection()
    jiras = conn.execute('SELECT * FROM jiras').fetchall()
    conn.close()
    return render_template('jiras.html', jiras=jiras)
    
    
@app.route('/pullRequests')
@login_required
def pullRequests():
    conn = get_db_connection()
    pullRequests = conn.execute('SELECT * FROM pullRequests').fetchall()
    conn.close()
    return render_template('pullRequests.html', pullRequests=pullRequests)


@app.route('/<int:post_id>')
@login_required
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/jiras/<int:jira_id>')
@login_required
def jira(jira_id):
    jira = get_jira(jira_id)
    return render_template('jira.html', jira=jira)


@app.route('/create', methods=('GET', 'POST'))
@login_required
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

    return render_template('create.html')

@app.route('/create-jira', methods=('GET', 'POST'))
@login_required
def create_jira():
    if request.method == 'POST':
        print(request.form)
        input = {}
        input['jira'] = {}
        input['jira']['type'] = request.form['type']
        input['jira']['title'] = request.form['title']
        input['jira']['pullRequestID'] = int(request.form['pullRequestID'])
        input['jira']['descriptions'] = request.form['descriptions']
        shouldApprove = approveJira(input)
        input['jira']['approve'] = 0
        if shouldApprove:
            input['jira']['approve'] = 1
            flash('JIRA got approved')
        else:
            flash('The JIRA failed the necessary policies')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO jiras (title, type, pullRequestID,descriptions,createdBy,approved) VALUES (?,?,?,?,?,?)',
            (input['jira']['title'],input['jira']['type'],input['jira']['pullRequestID'],input['jira']['descriptions'],logged_user['username'],input['jira']['approve']))
        conn.commit()
        conn.close()
        return redirect(url_for('jiras'))

    return render_template('create_jira.html')

@app.route('/create-pr', methods=('GET', 'POST'))
@login_required
def create_pr():
    if request.method == 'POST':
        title = request.form['title']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO pullRequests (title, createdBy) VALUES (?, ?)',
                         (title, logged_user['username']))
            conn.commit()
            conn.close()
            return redirect(url_for('pullRequests'))

    return render_template('create_pr.html')

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
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? and password = ?',(username,password)).fetchone()
        conn.close()
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
@login_required
def logout():
    global logged_user
    logged_user = None
    flash('Successfully Logged Out')
    return redirect(url_for('loginUser'))

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
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
@login_required
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))
