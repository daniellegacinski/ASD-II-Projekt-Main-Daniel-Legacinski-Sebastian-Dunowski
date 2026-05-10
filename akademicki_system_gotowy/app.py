from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date, time, timedelta
import sqlite3, os, csv, io

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'academic.db')

app = Flask(__name__)
app.secret_key = 'demo-secret-change-in-production'

ROLES = ('ADMINISTRATOR', 'PROWADZACY', 'STUDENT')
ATTENDANCE_POINTS = {'PRESENT': 1.0, 'LATE': 0.5, 'ABSENT': 0.0}
GRADE_VALUES = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    cur = con.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('ADMINISTRATOR','PROWADZACY','STUDENT'))
    );
    CREATE TABLE IF NOT EXISTS semesters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('OPEN','CLOSED'))
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        semester_id INTEGER NOT NULL,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(semester_id) REFERENCES semesters(id)
    );
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        UNIQUE(student_id, group_id),
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    );
    CREATE TABLE IF NOT EXISTS teacher_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        UNIQUE(teacher_id, group_id),
        FOREIGN KEY(teacher_id) REFERENCES users(id),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    );
    CREATE TABLE IF NOT EXISTS meeting_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        weekday INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        frequency_weeks INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(group_id) REFERENCES groups(id)
    );
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        meeting_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('STANDARD','CANCELLED','RESCHEDULED','EXTRA')),
        topic TEXT,
        FOREIGN KEY(group_id) REFERENCES groups(id)
    );
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('PRESENT','LATE','ABSENT','EXCUSED')),
        UNIQUE(meeting_id, student_id),
        FOREIGN KEY(meeting_id) REFERENCES meetings(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS grade_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        weight_percent INTEGER NOT NULL,
        UNIQUE(group_id, name),
        FOREIGN KEY(group_id) REFERENCES groups(id)
    );
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        value REAL NOT NULL CHECK(value IN (2.0,2.5,3.0,3.5,4.0,4.5,5.0)),
        UNIQUE(category_id, student_id),
        FOREIGN KEY(category_id) REFERENCES grade_categories(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    );
    ''')
    con.commit()
    if cur.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        seed_demo(con)
    con.close()


def seed_demo(con):
    cur = con.cursor()
    users = [
        ('Admin Systemu', 'admin@demo.pl', 'admin123', 'ADMINISTRATOR'),
        ('Dr Anna Kowalska', 'anna@demo.pl', 'teacher123', 'PROWADZACY'),
        ('Mgr Piotr Nowak', 'piotr@demo.pl', 'teacher123', 'PROWADZACY'),
        ('Daniel Legacinski', 'daniel@demo.pl', 'student123', 'STUDENT'),
        ('Maria Wisniewska', 'maria@demo.pl', 'student123', 'STUDENT'),
        ('Jan Zielinski', 'jan@demo.pl', 'student123', 'STUDENT'),
        ('Ola Kaminska', 'ola@demo.pl', 'student123', 'STUDENT'),
        ('Tomasz Lewandowski', 'tomek@demo.pl', 'student123', 'STUDENT'),
        ('Karolina Mazur', 'karolina@demo.pl', 'student123', 'STUDENT'),
        ('Pawel Wozniak', 'pawel@demo.pl', 'student123', 'STUDENT'),
        ('Ewa Dabrowska', 'ewa@demo.pl', 'student123', 'STUDENT'),
    ]
    for name, email, pwd, role in users:
        cur.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)', (name,email,generate_password_hash(pwd),role))
    cur.execute('INSERT INTO semesters(name,status) VALUES(?,?)', ('Semestr letni 2026','OPEN'))
    cur.execute('INSERT INTO semesters(name,status) VALUES(?,?)', ('Semestr zimowy 2025/2026','CLOSED'))
    cur.execute('INSERT INTO courses(name,code) VALUES(?,?)', ('Programowanie aplikacji webowych','PAW'))
    cur.execute('INSERT INTO courses(name,code) VALUES(?,?)', ('Bazy danych','BD'))
    cur.execute('INSERT INTO groups(name,course_id,semester_id) VALUES(?,?,?)', ('PAW-LAB-1',1,1))
    cur.execute('INSERT INTO groups(name,course_id,semester_id) VALUES(?,?,?)', ('BD-LAB-1',2,1))
    cur.execute('INSERT INTO groups(name,course_id,semester_id) VALUES(?,?,?)', ('PAW-ARCH',1,2))
    for student_id in range(4,12):
        cur.execute('INSERT INTO enrollments(student_id,group_id) VALUES(?,?)', (student_id,1))
        if student_id in range(4,9): cur.execute('INSERT INTO enrollments(student_id,group_id) VALUES(?,?)', (student_id,2))
    cur.execute('INSERT INTO teacher_groups(teacher_id,group_id) VALUES(?,?)', (2,1))
    cur.execute('INSERT INTO teacher_groups(teacher_id,group_id) VALUES(?,?)', (3,2))
    for gid in (1,2):
        cats = [('Kolokwium',40),('Projekt',40),('Aktywnosc',20)]
        for c in cats: cur.execute('INSERT INTO grade_categories(group_id,name,weight_percent) VALUES(?,?,?)', (gid,c[0],c[1]))
    con.commit()
    generate_meetings(con, 1, date(2026,3,2), date(2026,4,20), 0, '09:00', 90, 1)
    generate_meetings(con, 2, date(2026,3,3), date(2026,4,21), 1, '11:00', 90, 1)
    cur = con.cursor()
    # mark one cancelled, one extra
    cur.execute("UPDATE meetings SET type='CANCELLED', topic='Odwołane przez prowadzącego' WHERE id=2")
    cur.execute("INSERT INTO meetings(group_id,meeting_date,start_time,duration_minutes,type,topic) VALUES(?,?,?,?,?,?)", (1,'2026-04-29','10:00',90,'EXTRA','Dodatkowe konsultacje'))
    students = [r['student_id'] for r in cur.execute('SELECT student_id FROM enrollments WHERE group_id=1')]
    meetings = cur.execute("SELECT * FROM meetings WHERE group_id=1 AND type!='CANCELLED'").fetchall()
    statuses = ['PRESENT','LATE','ABSENT','EXCUSED']
    for mi,m in enumerate(meetings):
        for si,sid in enumerate(students):
            status = statuses[(mi+si) % len(statuses)] if si in (2,5) else ('PRESENT' if (mi+si)%5 else 'LATE')
            cur.execute('INSERT OR IGNORE INTO attendance(meeting_id,student_id,status) VALUES(?,?,?)', (m['id'],sid,status))
    cats = cur.execute('SELECT * FROM grade_categories WHERE group_id=1').fetchall()
    vals = [5.0,4.5,4.0,3.5,3.0,2.5,5.0,4.0]
    for ci,cat in enumerate(cats):
        for i,sid in enumerate(students):
            cur.execute('INSERT OR IGNORE INTO grades(category_id,student_id,value) VALUES(?,?,?)', (cat['id'],sid,vals[(i+ci)%len(vals)]))
    con.commit()


def semester_open(con, group_id):
    row = con.execute('SELECT s.status FROM groups g JOIN semesters s ON s.id=g.semester_id WHERE g.id=?', (group_id,)).fetchone()
    return row and row['status']=='OPEN'


def generate_meetings(con, group_id, start_d, end_d, weekday, start_t, duration, freq):
    cur = con.cursor()
    cur.execute('INSERT INTO meeting_rules(group_id,weekday,start_time,duration_minutes,start_date,end_date,frequency_weeks) VALUES(?,?,?,?,?,?,?)',
                (group_id,weekday,start_t,duration,start_d.isoformat(),end_d.isoformat(),freq))
    d = start_d
    while d.weekday() != weekday: d += timedelta(days=1)
    while d <= end_d:
        cur.execute('INSERT INTO meetings(group_id,meeting_date,start_time,duration_minutes,type,topic) VALUES(?,?,?,?,?,?)',
                    (group_id,d.isoformat(),start_t,duration,'STANDARD','Zajęcia cykliczne'))
        d += timedelta(weeks=freq)
    con.commit()


def current_user():
    if 'user_id' not in session: return None
    con = db(); u = con.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone(); con.close(); return u

@app.context_processor
def inject(): return {'me': current_user()}

def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user(): return redirect(url_for('login'))
        return fn(*a, **kw)
    return wrapper

def require_roles(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            u = current_user()
            if not u or u['role'] not in roles:
                flash('Brak uprawnień do tej operacji.', 'error'); return redirect(url_for('dashboard'))
            return fn(*a, **kw)
        return wrapper
    return deco


def allowed_groups(con, user):
    if user['role']=='ADMINISTRATOR':
        return con.execute('SELECT g.*, c.name course, s.name semester, s.status FROM groups g JOIN courses c ON c.id=g.course_id JOIN semesters s ON s.id=g.semester_id ORDER BY g.id').fetchall()
    if user['role']=='PROWADZACY':
        return con.execute('SELECT g.*, c.name course, s.name semester, s.status FROM groups g JOIN teacher_groups tg ON tg.group_id=g.id JOIN courses c ON c.id=g.course_id JOIN semesters s ON s.id=g.semester_id WHERE tg.teacher_id=?', (user['id'],)).fetchall()
    return con.execute('SELECT g.*, c.name course, s.name semester, s.status FROM groups g JOIN enrollments e ON e.group_id=g.id JOIN courses c ON c.id=g.course_id JOIN semesters s ON s.id=g.semester_id WHERE e.student_id=?', (user['id'],)).fetchall()


def check_group_access(con, group_id, user):
    return any(g['id']==group_id for g in allowed_groups(con,user))


def attendance_percent(con, student_id, group_id):
    rows = con.execute('''SELECT a.status FROM attendance a JOIN meetings m ON m.id=a.meeting_id
                          WHERE a.student_id=? AND m.group_id=? AND m.type!='CANCELLED' ''', (student_id,group_id)).fetchall()
    denom = 0; points = 0.0
    for r in rows:
        if r['status']=='EXCUSED': continue
        denom += 1; points += ATTENDANCE_POINTS.get(r['status'],0)
    if denom == 0: return None
    return round(points / denom * 100, 2)


def average_grade(con, student_id, group_id):
    cats = con.execute('SELECT * FROM grade_categories WHERE group_id=?', (group_id,)).fetchall()
    total=0; weight_sum=0
    for c in cats:
        gr = con.execute('SELECT value FROM grades WHERE category_id=? AND student_id=?', (c['id'],student_id)).fetchone()
        if not gr: continue
        total += gr['value'] * c['weight_percent']; weight_sum += c['weight_percent']
    if weight_sum==0: return None
    return round(total / weight_sum, 2)

@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user() else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        con=db(); u=con.execute('SELECT * FROM users WHERE email=?', (request.form['email'],)).fetchone(); con.close()
        if u and check_password_hash(u['password_hash'], request.form['password']):
            session['user_id']=u['id']; return redirect(url_for('dashboard'))
        flash('Niepoprawny login lub hasło.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    u=current_user(); con=db(); groups=allowed_groups(con,u)
    stats={'groups':len(groups), 'students':con.execute("SELECT COUNT(*) c FROM users WHERE role='STUDENT'").fetchone()['c'], 'meetings':con.execute('SELECT COUNT(*) c FROM meetings').fetchone()['c']}
    con.close(); return render_template('dashboard.html', groups=groups, stats=stats)

@app.route('/group/<int:group_id>')
@login_required
def group_detail(group_id):
    u=current_user(); con=db()
    if not check_group_access(con,group_id,u): con.close(); flash('Nie masz dostępu do tej grupy.', 'error'); return redirect(url_for('dashboard'))
    group=con.execute('SELECT g.*, c.name course, s.name semester, s.status FROM groups g JOIN courses c ON c.id=g.course_id JOIN semesters s ON s.id=g.semester_id WHERE g.id=?',(group_id,)).fetchone()
    students=con.execute('SELECT u.* FROM users u JOIN enrollments e ON e.student_id=u.id WHERE e.group_id=? ORDER BY u.name',(group_id,)).fetchall()
    meetings=con.execute('SELECT * FROM meetings WHERE group_id=? ORDER BY meeting_date,start_time',(group_id,)).fetchall()
    cats=con.execute('SELECT * FROM grade_categories WHERE group_id=?',(group_id,)).fetchall()
    data=[]
    for s in students:
        data.append({'student':s,'attendance':attendance_percent(con,s['id'],group_id),'risk': (attendance_percent(con,s['id'],group_id) is not None and attendance_percent(con,s['id'],group_id)<60 and len(meetings)>=3), 'avg':average_grade(con,s['id'],group_id)})
    con.close(); return render_template('group.html', group=group, students=data, meetings=meetings, cats=cats, grades=GRADE_VALUES)

@app.route('/semester/<int:semester_id>/close', methods=['POST'])
@login_required
@require_roles('ADMINISTRATOR')
def close_semester(semester_id):
    con=db(); con.execute("UPDATE semesters SET status='CLOSED' WHERE id=?",(semester_id,)); con.commit(); con.close(); flash('Semestr zamknięty. Edycja danych została zablokowana.', 'ok'); return redirect(url_for('dashboard'))

@app.route('/meeting/create/<int:group_id>', methods=['POST'])
@login_required
@require_roles('ADMINISTRATOR','PROWADZACY')
def create_meeting(group_id):
    u=current_user(); con=db()
    if not check_group_access(con,group_id,u) or not semester_open(con,group_id): con.close(); flash('Brak dostępu albo semestr zamknięty.', 'error'); return redirect(url_for('group_detail',group_id=group_id))
    con.execute('INSERT INTO meetings(group_id,meeting_date,start_time,duration_minutes,type,topic) VALUES(?,?,?,?,?,?)', (group_id,request.form['date'],request.form['time'],int(request.form['duration']),request.form['type'],request.form.get('topic','')))
    con.commit(); con.close(); flash('Spotkanie dodane.', 'ok'); return redirect(url_for('group_detail',group_id=group_id))

@app.route('/attendance/<int:group_id>', methods=['POST'])
@login_required
@require_roles('ADMINISTRATOR','PROWADZACY')
def save_attendance(group_id):
    u=current_user(); con=db()
    if not check_group_access(con,group_id,u) or not semester_open(con,group_id): con.close(); flash('Brak dostępu albo semestr zamknięty.', 'error'); return redirect(url_for('group_detail',group_id=group_id))
    meeting_id=int(request.form['meeting_id'])
    for key,value in request.form.items():
        if key.startswith('student_'):
            sid=int(key.split('_')[1]); con.execute('INSERT OR REPLACE INTO attendance(meeting_id,student_id,status) VALUES(?,?,?)',(meeting_id,sid,value))
    con.commit(); con.close(); flash('Frekwencja zapisana.', 'ok'); return redirect(url_for('group_detail',group_id=group_id))

@app.route('/grades/<int:group_id>', methods=['POST'])
@login_required
@require_roles('ADMINISTRATOR','PROWADZACY')
def save_grades(group_id):
    u=current_user(); con=db()
    if not check_group_access(con,group_id,u) or not semester_open(con,group_id): con.close(); flash('Brak dostępu albo semestr zamknięty.', 'error'); return redirect(url_for('group_detail',group_id=group_id))
    total = sum([r['weight_percent'] for r in con.execute('SELECT weight_percent FROM grade_categories WHERE group_id=?',(group_id,)).fetchall()])
    if total != 100: flash('Suma wag kategorii musi wynosić 100%.', 'error'); con.close(); return redirect(url_for('group_detail',group_id=group_id))
    for key,value in request.form.items():
        if key.startswith('grade_') and value:
            _,cat,sid=key.split('_'); con.execute('INSERT OR REPLACE INTO grades(category_id,student_id,value) VALUES(?,?,?)',(int(cat),int(sid),float(value)))
    con.commit(); con.close(); flash('Oceny zapisane.', 'ok'); return redirect(url_for('group_detail',group_id=group_id))

@app.route('/export/<int:group_id>.csv')
@login_required
def export_csv(group_id):
    u=current_user(); con=db()
    if not check_group_access(con,group_id,u): con.close(); flash('Brak dostępu.', 'error'); return redirect(url_for('dashboard'))
    out=io.StringIO(); writer=csv.writer(out)
    writer.writerow(['Student','Frekwencja %','AT_RISK','Średnia ważona'])
    students=con.execute('SELECT u.* FROM users u JOIN enrollments e ON e.student_id=u.id WHERE e.group_id=? ORDER BY u.name',(group_id,)).fetchall()
    for s in students:
        att=attendance_percent(con,s['id'],group_id); avg=average_grade(con,s['id'],group_id); risk=(att is not None and att<60)
        writer.writerow([s['name'], att if att is not None else 'N/A', 'AT_RISK' if risk else 'OK', avg if avg is not None else 'N/A'])
    con.close(); return Response(out.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=export_grupa_%s.csv'%group_id})

if __name__ == '__main__':
    init_db(); app.run(debug=True)
