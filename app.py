from flask import *
import sqlite3

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('./project.db')
    db = conn.cursor()
    db.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["POST"])
def login():
    name = request.form.get('name')
    password = request.form.get('password')
    
    conn = sqlite3.connect('project.db')
    db = conn.cursor()
    db.execute("INSERT INTO users (name, password) VALUES (?,?)", (name, password))
    conn.commit()
    conn.close()
    return redirect('/homepage')

@app.route('/homepage')
def hello():
    # registerants = db.execute("SELECT * FROM users")
    return render_template('homepage.html')


if __name__ == '__main__':
    create_database()
    app.run(debug=True)