from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

# 비밀 키 설정 (세션 관리를 위해 필요)
app.secret_key = 'secret_key'

# MySQL 설정
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '1234'
DB_NAME = 'flask_website_db'

# 데이터베이스 연결 함수
def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8')

# 기본 경로 설정
@app.route('/')
def home():
    return '''
    <h1>Welcome to the Flask App!</h1>
    <p><a href="/register">회원가입</a> | <a href="/login">로그인</a></p>
    '''

# 회원가입 경로
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # 데이터 유효성 검사
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!")
            return redirect(url_for('register'))
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!")
            return redirect(url_for('register'))

        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 중복 사용자명/이메일 확인
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        account = cursor.fetchone()
        
        if account:
            flash("Username or Email already exists!")  # 중복 계정이 존재하는 경우 오류 메시지
            return redirect(url_for('register'))
        
        # 비밀번호 해싱 및 사용자 정보 저장
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', 
                       (username, hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# 로그인 경로
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 사용자명으로 계정 조회
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # 계정이 존재하지 않는 경우
        if not account:
            flash("Account does not exist. Please register first.")
            return redirect(url_for('login'))
        
        # 비밀번호 확인
        if not check_password_hash(account['password'], password):
            flash("Incorrect password. Please try again.")
            return redirect(url_for('login'))
        
        # 로그인 성공 시 세션에 정보 저장
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        flash(f"Hello, {session['username']}! You are logged in.")
        return redirect(url_for('home'))

    return render_template('login.html')

# 데이터베이스 연결 테스트 경로
@app.route('/db_test')
def db_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # 간단한 쿼리 실행
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"MySQL 연결 성공! 결과: {result}"
    except Exception as e:
        return f"MySQL 연결 실패: {e}"

if __name__ == "__main__":
    app.run(port=5001, debug=True)  # 5001 포트로 변경 및 debug 모드 설정
