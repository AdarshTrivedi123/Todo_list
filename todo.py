from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import re

app = Flask(__name__)
app.secret_key = "ftygf536467trfr5"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'todo_register'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/reg')
def reg():
    msg = ''
    return render_template('register.html', msg=msg)


@app.route('/in')
def inpage():
    msg = ''
    return render_template('login.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def register():
    cur = mysql.connection.cursor()
    if request.method == 'POST' and 'nm' in request.form and 'email' in request.form and 'pas' in request.form:
        msg = ''
        nm = request.form['nm']
        email = request.form['email']
        pas = request.form['pas']
        cur.execute("select* from user where userid= %s", (nm, ))
        mysql.connection.commit()
        account = cur.fetchone()
        if account:
            msg = 'Account already exists'
            return render_template('register.html', msg=msg)
        elif not re.match("^[A-Za-z0-9_-]*$", nm):
            msg = "username can have only numbers and alphabets"
            return render_template('register.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template('register.html', msg=msg)
        elif len(pas) < 6:
            msg = 'Password must be atleast 6 character long'
            return render_template('register.html', msg=msg)
        else:
            cur.execute("insert into user value(%s,%s,%s)", (nm, email, pas))
            mysql.connection.commit()
            cur.close()
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Fill the details to register'
        return render_template('registration.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    msg = ''
    if request.method == 'POST':
        name = request.form['nm']
        pasw = request.form['pas']
        cur.execute("select* from user where userid=%s", (name, ))
        mysql.connection.commit()
        logdata = cur.fetchone()
        if logdata:
            cur.execute(
                "select* from user where userid=%s and pwd=%s", (name, pasw, ))
            mysql.connection.commit()
            acc = cur.fetchone()
            if acc:
                session['id'] = name
                # return 'suc'
                return render_template('ask.html', name=name)
            else:
                msg = 'Wrong Password'
        else:
            msg = 'This user name is not registered'
    return render_template('login.html', msg=msg)

# task_id=0


@app.route('/add', methods=['GET', 'POST'])
def add():     
    tname = request.form['tname']
    dis = request.form['dis']
    status = request.form['status']
    id = session.get("id")
    cur = mysql.connection.cursor()
#    task_id=task_id+1
    cur.execute("insert into task (id,task_name,des,status) values(%s,%s,%s,%s)",
                (id, tname, dis, status, ))
    mysql.connection.commit()
    cur.execute(
        "select task_name,des,status,task_id from task where id=%s", (id, ))
    mysql.connection.commit()
    data = cur.fetchall()
    return render_template("list.html", data=data)


@app.route('/view')
def view():
    cur = mysql.connection.cursor()
    id = session.get("id")
    cur.execute(
        "select task_name,des,status,task_id from task where id=%s", (id, ))
    mysql.connection.commit()
    data = cur.fetchall()
    return render_template("list.html", data=data)

@app.route('/delete/<int:tid>')
def delete(tid):
    cur = mysql.connection.cursor()
    cur.execute("delete from task where task_id=%s", (tid, ))
    mysql.connection.commit()
    return redirect(url_for('view'))


@app.route('/edit/<int:tid>')
def edit(tid):
    return render_template("edit.html",task_id=tid)


@app.route('/changes/<int:tid>', methods=['GET','POST'])
def changes(tid):
    if request.method=='POST':
      cur=mysql.connection.cursor()
      cur.execute("select* from task where task_id=%s",(tid, ) )
      mysql.connection.commit()
      detail=cur.fetchone()
      tname = request.form['tname']
      if tname=="":
         cur.execute("select task_name from task where task_id=%s",(tid, ) )
         mysql.connection.commit()
         tname=cur.fetchone()
      dis = request.form['dis']
      if dis=="":
         cur.execute("select des from task where task_id=%s",(tid, ) )
         mysql.connection.commit()
         dis=cur.fetchone()
      status = request.form['status']
      if status=="":
         cur.execute("select status from task where task_id=%s",(tid, ) )
         mysql.connection.commit()
         status=cur.fetchone()

      cur=mysql.connection.cursor()
      cur.execute("update task set task_name=%s,des=%s,status=%s where task_id=%s",(tname,dis,status,tid, ))
      mysql.connection.commit()
      return redirect(url_for('view'))

app.run(debug=True)
