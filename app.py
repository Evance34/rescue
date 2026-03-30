
from flask import Flask,request,render_template,redirect,session
import sqlite3,os,ssl,smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'secret'

def db():
    return sqlite3.connect('cases.db')

conn = db()
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS cases(
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    desc TEXT,
    file TEXT,
    status TEXT
)''')
conn.commit()
conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    f = request.files['file']
    fname = f.filename
    if fname:
        f.save(os.path.join('uploads', fname))

    d = request.form
    conn = db()
    cur = conn.cursor()
    cur.execute('INSERT INTO cases(name,email,phone,desc,file,status) VALUES(?,?,?,?,?,?)',
                (d['name'], d['email'], d['phone'], d['desc'], fname, 'Pending'))
    conn.commit()
    conn.close()

    # EMAIL
    msg = MIMEText(f"New report from {d['name']} {d['email']}")
    msg['Subject'] = 'New Report'
    msg['From'] = os.getenv('GMAIL_USER')
    msg['To'] = os.getenv('GMAIL_USER')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as s:
        s.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASS'))
        s.send_message(msg)

    return 'Report submitted.'

@app.route('/admin')
def admin():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form['user'] == 'admin' and request.form['pw'] == 'password':
        session['admin'] = True
        return redirect('/dashboard')
    return 'Invalid login'

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    conn = db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM cases')
    rows = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', cases=rows)

if __name__ == '__main__':
    app.run()
