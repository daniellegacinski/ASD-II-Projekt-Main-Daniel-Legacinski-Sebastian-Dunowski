import os, tempfile, importlib

def test_attendance_and_average():
    import app as a
    fd, path = tempfile.mkstemp(); os.close(fd)
    old = a.DB_PATH; a.DB_PATH = path
    a.init_db(); con = a.db()
    assert a.attendance_percent(con, 4, 1) is not None
    assert a.average_grade(con, 4, 1) is not None
    assert con.execute('SELECT COUNT(*) FROM users WHERE role="STUDENT"').fetchone()[0] >= 8
    assert con.execute('SELECT COUNT(*) FROM courses').fetchone()[0] >= 2
    weights = sum(r['weight_percent'] for r in con.execute('SELECT weight_percent FROM grade_categories WHERE group_id=1'))
    assert weights == 100
    con.close(); a.DB_PATH = old; os.remove(path)

def test_login_page():
    import app as a
    fd, path = tempfile.mkstemp(); os.close(fd)
    old = a.DB_PATH; a.DB_PATH = path; a.init_db(); a.app.config['TESTING']=True
    c = a.app.test_client(); res = c.get('/login')
    assert res.status_code == 200
    res = c.post('/login', data={'email':'admin@demo.pl','password':'admin123'}, follow_redirects=True)
    assert b'Panel' in res.data
    a.DB_PATH = old; os.remove(path)
