from flask import *
from flask_session import Session
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOlDER = 'static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOlDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

fitness = ["plank", "lunge", "crunch", "squat"]
muscular = ["deadlift", "bench", "split", "leg"]

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET","POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            flash("must provide username")
            return redirect("/")

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            flash("must provide password")
            return redirect("/")

        # Query database for username
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        rows = db.execute("SELECT * FROM users WHERE name = ?", (username,))
        rows = rows.fetchall()
        conn.commit()
        conn.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or (rows[0][2] != password):
            flash("invalid username and/or password")
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        name = db.execute("SELECT user_name FROM users WHERE id = ?", (session["user_id"],))
        name = name.fetchall()
        conn.commit()
        conn.close()

        session['user_name'] = name[0][0]

        # Redirect user to home page
        return redirect("/homepage")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")

@app.route('/register', methods=["GET","POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            flash("must provide username")
            return redirect("/register")

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            flash("must provide password")
            return redirect("/register")

        # Ensure password confirmation was submitted
        pass_confirm = request.form.get("confirmation")
        if not pass_confirm:
            flash("must provide password confirmation")
            return redirect("/register")

        # Ensure that passwords match
        elif password != pass_confirm:
            flash("The passwords do not match")
            return redirect("/register")

        #insert the new user into users
        try:
            conn = sqlite3.connect('./project.db')
            db = conn.cursor()
            db.execute("INSERT INTO users (name, password) VALUES (?,?)", (username, password))
            new_user = db.execute("SELECT id FROM users WHERE name = ? and password = ?", (username, password))
            new_user = new_user.fetchall()
            conn.commit()
            conn.close()
        except:
            flash("The username already exists")
            return redirect("/register")

        session["user_id"] = new_user[0][0]

        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        name = db.execute("SELECT user_name FROM users WHERE id = ?", (session["user_id"],))
        name = name.fetchall()
        conn.commit()
        conn.close()

        session['user_name'] = name[0][0]

        # Redirect user to home page
        return redirect("/homepage")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/homepage', methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        username = request.form.get("name")

        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("UPDATE users SET user_name = ? WHERE id = ?", (username, session["user_id"]))
        conn.commit()
        conn.close()

        session['user_name'] = username
        return redirect('/edit')
    
    if session['user_name']:
        name = session['user_name']
    else:
        name = 'Your Name'

    fitness_progress = 0
    for i in fitness:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        check = db.execute(f"SELECT id FROM {i} WHERE statues = 'completed' and user_id = ?", (session["user_id"],))
        check = check.fetchall()
        conn.commit()
        conn.close()

        if check:
            fitness_progress += 10

    muscular_progress = 0
    for i in muscular:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        check = db.execute(f"SELECT id FROM {i} WHERE statues = 'completed' and user_id = ?", (session["user_id"],))
        check = check.fetchall()
        conn.commit()
        conn.close()

        if check:
            muscular_progress += 10

    conn = sqlite3.connect('./project.db')
    db = conn.cursor()
    profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
    profile_pic = profile_pic.fetchall()
    conn.commit()
    conn.close()

    return render_template('homepage.html', fitness_progress=int((fitness_progress / 40) * 100) , muscular_progress=int((muscular_progress / 40) * 100), profile_pic=profile_pic[0][0], name=name)

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/edit')
        
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect('/edit')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect('./project.db')
            db = conn.cursor()
            db.execute("UPDATE users SET pic = ? WHERE id = ?", (('uploads/' + filename), session['user_id']))
            profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
            profile_pic = profile_pic.fetchall()
            conn.commit()
            conn.close()

            if session['user_name']:
                name = session['user_name']
            else:
                name = 'Your Name'

            flash('Image successfully uploaded')
            return render_template("edit.html", profile_pic=profile_pic[0][0], name=name)
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif -')
            return redirect('/edit')

    conn = sqlite3.connect('./project.db')
    db = conn.cursor()
    profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
    profile_pic = profile_pic.fetchall()
    conn.commit()
    conn.close()

    if session['user_name']:
        name = session['user_name']
    else:
        name = 'Your Name'

    return render_template("edit.html", profile_pic=profile_pic[0][0], name=name)

@app.route('/activity')
def activity():
    conn = sqlite3.connect('./project.db')
    db = conn.cursor()
    profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
    profile_pic = profile_pic.fetchall()
    conn.commit()
    conn.close()

    if session['user_name']:
        name = session['user_name']
    else:
        name = 'Your Name'

    return render_template('activity.html', profile_pic=profile_pic[0][0], name=name)

@app.route('/plank', methods=["GET", "POST"])
def plank():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO plank (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        plank_statues = db.execute("SELECT statues FROM plank WHERE user_id = ?", (session["user_id"],))
        plank_statues = plank_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('plank.html', plank_statues=plank_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        plank_statues = db.execute("SELECT statues FROM plank WHERE user_id = ?", (session["user_id"],))
        plank_statues = plank_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('plank.html', plank_statues=plank_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/lunge', methods=["GET", "POST"])
def lunge():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO lunge (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        lunge_statues = db.execute("SELECT statues FROM lunge WHERE user_id = ?", (session["user_id"],))
        lunge_statues = lunge_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()
        
        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('lunge.html', lunge_statues=lunge_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        lunge_statues = db.execute("SELECT statues FROM lunge WHERE user_id = ?", (session["user_id"],))
        lunge_statues = lunge_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('lunge.html', lunge_statues=lunge_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/crunch', methods=["GET", "POST"])
def crunch():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO crunch (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        crunch_statues = db.execute("SELECT statues FROM crunch WHERE user_id = ?", (session["user_id"],))
        crunch_statues = crunch_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('crunch.html', crunch_statues=crunch_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        crunch_statues = db.execute("SELECT statues FROM crunch WHERE user_id = ?", (session["user_id"],))
        crunch_statues = crunch_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('crunch.html', crunch_statues=crunch_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/squat', methods=["GET", "POST"])
def squat():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO squat (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        squat_statues = db.execute("SELECT statues FROM squat WHERE user_id = ?", (session["user_id"],))
        squat_statues = squat_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('squat.html', squat_statues=squat_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        squat_statues = db.execute("SELECT statues FROM squat WHERE user_id = ?", (session["user_id"],))
        squat_statues = squat_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('squat.html', squat_statues=squat_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/dlift', methods=["GET", "POST"])
def dlift():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO deadlift (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        dlift_statues = db.execute("SELECT statues FROM deadlift WHERE user_id = ?", (session["user_id"],))
        dlift_statues = dlift_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('deadlift.html', dlift_statues=dlift_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        dlift_statues = db.execute("SELECT statues FROM deadlift WHERE user_id = ?", (session["user_id"],))
        dlift_statues = dlift_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('deadlift.html', dlift_statues=dlift_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/bench', methods=["GET", "POST"])
def bench():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO bench (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        bench_statues = db.execute("SELECT statues FROM bench WHERE user_id = ?", (session["user_id"],))
        bench_statues = bench_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('bench.html', bench_statues=bench_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        bench_statues = db.execute("SELECT statues FROM bench WHERE user_id = ?", (session["user_id"],))
        bench_statues = bench_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('bench.html', bench_statues=bench_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/split', methods=["GET", "POST"])
def split():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO split (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        split_statues = db.execute("SELECT statues FROM split WHERE user_id = ?", (session["user_id"],))
        split_statues = split_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('split.html', split_statues=split_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        split_statues = db.execute("SELECT statues FROM split WHERE user_id = ?", (session["user_id"],))
        split_statues = split_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('split.html', split_statues=split_statues, profile_pic=profile_pic[0][0], name=name)

@app.route('/leg', methods=["GET", "POST"])
def leg():
    if request.method == "POST":
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        db.execute("INSERT INTO leg (user_id, statues) VALUES (?,?)", (session["user_id"], "completed"))
        leg_statues = db.execute("SELECT statues FROM leg WHERE user_id = ?", (session["user_id"],))
        leg_statues = leg_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('leg.html', leg_statues=leg_statues, profile_pic=profile_pic[0][0], name=name)
    else:
        conn = sqlite3.connect('./project.db')
        db = conn.cursor()
        leg_statues = db.execute("SELECT statues FROM leg WHERE user_id = ?", (session["user_id"],))
        leg_statues = leg_statues.fetchall()
        profile_pic = db.execute("SELECT pic FROM users WHERE id = ?", (session['user_id'],))
        profile_pic = profile_pic.fetchall()
        conn.commit()
        conn.close()

        if session['user_name']:
            name = session['user_name']
        else:
            name = 'Your Name'

        return render_template('leg.html', leg_statues=leg_statues, profile_pic=profile_pic[0][0], name=name)

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)