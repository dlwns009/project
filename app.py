from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 비밀 키 설정 (세션 관리를 위해 필요)
app.secret_key = 'your_secret_key'

# MySQL 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'flask_website_db'
app.config['MYSQL_SSL_DISABLED'] = True
app.config['MYSQL_SSL_CA'] = ''  # SSL CA 인증서 경로 비우기
app.config['MYSQL_SSL_CERT'] = ''  # SSL 인증서 경로 비우기
app.config['MYSQL_SSL_KEY'] = ''  # SSL 키 경로 비우기

# MySQL 초기화
mysql = MySQL(app)

# 기본 경로 설정
@app.route('/')
def home():
    return '''
    <h1>Welcome to the Flask App!</h1>
    <p><a href="/register">회원가입</a> | <a href="/login">로그인</a></p>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # 데이터 유효성 검사 (간단한 예)
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return "Invalid email address!"
        elif not re.match(r'[A-Za-z0-9]+', username):
            return "Username must contain only characters and numbers!"

        # 중복 사용자명/이메일 확인
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        account = cursor.fetchone()
        
        if account:
            return "Username or Email already exists!"  # 중복 계정이 존재하는 경우 오류 메시지
        
        # 비밀번호 해싱 및 사용자 정보 저장
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', 
                       (username, hashed_password, email))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login'))  # 회원가입 성공 시 로그인 페이지로 리디렉션

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 사용자명으로 계정 조회
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.close()
        
        # 계정이 존재하지 않는 경우
        if not account:
            return "Account does not exist. Please register first."
        
        # 비밀번호 확인
        if not check_password_hash(account['password'], password):
            return "Incorrect password. Please try again."
        
        # 로그인 성공 시 세션에 정보 저장
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return f"Hello, {session['username']}! You are logged in."  # 로그인 성공 메시지

    return render_template('login.html')

@app.route('/db_test') #연결상태확인
def db_test():
    try:
        cursor = mysql.connection.cursor()  # MySQL 연결 시도
        cursor.execute("SELECT 1")  # 간단한 쿼리 실행
        result = cursor.fetchone()
        cursor.close()
        return f"MySQL 연결 성공! 결과: {result}"
    except Exception as e:
        return f"MySQL 연결 실패: {e}"

if __name__ == "__main__":
    app.run(port=5001, debug=True)  # 5001 포트로 변경 및 debug 모드 설정
