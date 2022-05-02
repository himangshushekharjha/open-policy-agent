import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password,permissions) VALUES (?, ?, ?)",
            ('sanjeev', 'sanjeev', 'IT_DEVELOPER IT_QA_ADMIN ADMIN')
            )

cur.execute("INSERT INTO users (username, password,permissions) VALUES (?, ?, ?)",
            ('himangshu', 'himangshu', 'IT_DEVELOPER IT_QA_ADMIN')
            )

cur.execute("INSERT INTO users (username, password,permissions) VALUES (?, ?, ?)",
            ('tathya', 'tathya', 'IT_QA_ADMIN')
            )

cur.execute("INSERT INTO users (username, password,permissions) VALUES (?, ?, ?)",
            ('pralave', 'pralave', 'ADMIN')
            )


cur.execute("INSERT INTO posts (title, content,createdBy) VALUES (?, ?, ?)",
            ('First Post', 'Content for the first post','himangshu')
            )

cur.execute("INSERT INTO posts (title, content, createdBy) VALUES (?, ?, ?)",
            ('Second Post', 'Content for the second post','sanjeev')
            )
cur.execute("INSERT INTO pullRequests (title, createdBy) VALUES (?,?)",
            ('This is the First Pull Request',"himangshu")
            )
cur.execute("INSERT INTO jiras (title, type, pullRequestID,descriptions,createdBy,approved) VALUES (?,?,?,?,?,?)",
            ('This is the First Requirement Jira','requirement',1,"This field is currently necessary for Requirements approval","himangshu",1)
            )


connection.commit()
connection.close()