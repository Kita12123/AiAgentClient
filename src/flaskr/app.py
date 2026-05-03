from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import uuid
from datetime import datetime

# import AI service factory from services
from services import get_ai_service

app = Flask(__name__)

# Simple SQLite DB in the flaskr directory
BASEDIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASEDIR, 'chat.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT (DATETIME('now'))
        );
    ''')
    conn.commit()
    conn.close()


# initialize DB on import
init_db()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET'])
def chat():
    return render_template('chat.html')


@app.route('/greet', methods=['POST'])
def greet():
    name = request.form.get('name', 'World').strip() or 'World'
    return render_template('greet.html', name=name)


@app.route('/api/chat', methods=['POST'])
def post_chat():
    try:
        body = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'invalid json'}), 400

    message = (body.get('message') or '').strip()
    session_id = body.get('session_id') or str(uuid.uuid4())

    if not message:
        return jsonify({'error': 'empty message'}), 400

    # call AI service (from services package)
    ai = get_ai_service()
    try:
        reply = ai.request_message(message)
    except Exception as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500

    # persist messages
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO chat_messages (session_id, role, message) VALUES (?, ?, ?)', (session_id, 'user', message))
    cur.execute('INSERT INTO chat_messages (session_id, role, message) VALUES (?, ?, ?)', (session_id, 'ai', reply))
    conn.commit()
    conn.close()

    return jsonify({'reply': reply, 'session_id': session_id})


@app.route('/api/chat/history', methods=['GET'])
def get_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT role, message, created_at FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
    rows = cur.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({'role': r['role'], 'message': r['message'], 'created_at': r['created_at']})

    return jsonify(history)
