import http.server
import json
import mysql.connector
import hashlib

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tej@shwini05',  # Replace with your MySQL password
    'database': 'Desi'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def handle_login(data):
    username = data.get('username')
    password = data.get('password')
    hashed_password = hash_password(password)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return json.dumps({'success': True, 'message': 'Login successful'}).encode('utf-8')
        else:
            return json.dumps({'success': False, 'message': 'Invalid username or password'}).encode('utf-8')
    else:
        return json.dumps({'success': False, 'message': 'Database connection error'}).encode('utf-8')

def handle_register(data):
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    hashed_password = hash_password(password)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO users (username, password, email, phone) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, hashed_password, email, phone))
            conn.commit()
            return json.dumps({'success': True, 'message': 'Registration successful'}).encode('utf-8')
        except mysql.connector.IntegrityError:
            return json.dumps({'success': False, 'message': 'Username or email already exists'}).encode('utf-8')
        except mysql.connector.Error as e:
            return json.dumps({'success': False, 'message': f'Database error: {e}'}).encode('utf-8')
        finally:
            cursor.close()
            conn.close()
    else:
        return json.dumps({'success': False, 'message': 'Database connection error'}).encode('utf-8')

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            response = handle_login(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response)
        elif self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            response = handle_register(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open('index.html', 'rb') as file:  # Serves index.html (your home page)
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        elif self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('login.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/register':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('register.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                with open('dishes.html', 'rb') as file:  # Serves index.html (your home page)
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, MyHandler)
    print('Starting server on port 8000...')
    httpd.serve_forever()