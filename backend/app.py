import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "mi-base-datos")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "todolist")

def get_db_connection():
    retries = 6
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
                cursor_factory=RealDictCursor
            )
            return conn
        except psycopg2.OperationalError:
            print("⚠️ Esperando base de datos...")
            retries -= 1
            time.sleep(3)
    raise Exception("❌ No se conectó a PostgreSQL.")

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, descrip, completed FROM tasks ORDER BY id DESC;")
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = data.get('title')
    descrip = data.get('descrip', 'Tarea registrada desde la App Web')
    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, descrip, completed) VALUES (%s, %s, False) RETURNING id;",
            (title, descrip)
        )
        new_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id, "title": title, "descrip": descrip, "completed": False}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not deleted:
            return jsonify({"error": "No existe"}), 404
        return jsonify({"message": "Eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
