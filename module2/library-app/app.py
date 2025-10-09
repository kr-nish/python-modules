import os
from dotenv import load_dotenv
import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


#loads .env file
load_dotenv()


#Access the values and store it in a variable


def get_db_connection():
    return psycopg2.connect(
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASS")
    )


# print(f"Connecting to DB {db_name} at {db_host}:{db_port} as {db_user}")

class LibraryHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body)

        conn = get_db_connection()
        cur = conn.cursor()

        if self.path == "/users": #Add a user
            cur.execute("INSERT into users (name, email) VALUES (%s,%s) RETURNING id",
                        (data["name"], data["email"]))
            user_id = cur.fetchone()[0]
            conn.commit()
            self._set_headers(201)
            self.wfile.write(json.dumps({"message": "User added", "id": user_id}).encode())
    def do_PUT(self): #Edit a user
        user_id = int(self.path.split("/")[-1])
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body)
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("UPDATE users SET name =%s, email=%s WHERE id =%s",
                    (data["name"], data["email"], user_id))
        conn.commit()
        cur.close()
        conn.close()
        self._set_headers(200)
        self.wfile.write(json.dumps({"message": "user has been updated!"}).encode())

    def do_DELETE(self): #delete a user
        user_id = int(self.path.split("/")[-1])
       
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM users WHERE id=%s RETURNING id",
                    (user_id,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result:
            self._set_headers(200)
            self.wfile.write(json.dumps({"message":"User deleted"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error":"User not found"}).encode())

#Server init
def run(server_class=HTTPServer, handler_class = LibraryHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Library API is running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()