from flask import Flask, request, jsonify
import sqlite3
import requests
import datetime

app = Flask(__name__)
DB_NAME = "traceability.db"
HORNET_URL = "http://localhost:14265"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_id TEXT UNIQUE,
            tag TEXT,
            content TEXT,
            timestamp TEXT,
            is_solid INTEGER DEFAULT 0,
            is_valid INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>IOTA Advanced Explorer & Traceability</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; background-color: #f4f6f9; color: #333; }
            h1 { color: #1a252f; margin-bottom: 5px; }
            p { color: #555; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #007bff; color: white; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
            tr:hover { background-color: #f1f1f1; }
            .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
            .badge-success { background: #28a745; color: white; }
            .badge-danger { background: #dc3545; color: white; }
        </style>
    </head>
    <body>
        <h1>IOTA Tangle - Observability & Traceability</h1>
        <p>Trazabilidad y validación en tiempo real de eventos registrados en la Tangle privada.</p>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Block ID</th>
                    <th>Tag</th>
                    <th>Contenido</th>
                    <th>Fecha / Hora</th>
                    <th>Solid</th>
                    <th>Valid</th>
                </tr>
            </thead>
            <tbody id="eventsTable"></tbody>
        </table>

        <script>
            async function loadMessages() {
                try {
                    const res = await fetch('/messages');
                    const data = await res.json();
                    const tbody = document.getElementById('eventsTable');
                    tbody.innerHTML = '';
                    data.forEach(msg => {
                        const row = `<tr>
                            <td>${msg.id}</td>
                            <td style="font-family: monospace; font-size: 13px;">${msg.block_id}</td>
                            <td><strong>${msg.tag}</strong></td>
                            <td><code>${msg.content}</code></td>
                            <td>${msg.timestamp}</td>
                            <td><span class="badge ${msg.is_solid ? 'badge-success' : 'badge-danger'}">${msg.is_solid ? 'YES' : 'NO'}</span></td>
                            <td><span class="badge ${msg.is_valid ? 'badge-success' : 'badge-danger'}">${msg.is_valid ? 'YES' : 'NO'}</span></td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });
                } catch (e) {
                    console.error("Error cargando mensajes:", e);
                }
            }
            loadMessages();
            setInterval(loadMessages, 3000);
        </script>
    </body>
    </html>
    '''

@app.route('/trace', methods=['POST'])
def save_and_verify_message():
    data = request.json
    block_id = data.get('block_id')
    tag = data.get('tag', 'general')
    content = str(data.get('message', {}))
    timestamp = datetime.datetime.now().isoformat()

    is_solid = 0
    is_valid = 0

    if block_id:
        try:
            meta_res = requests.get(f"{HORNET_URL}/api/core/v2/blocks/{block_id}/metadata")
            if meta_res.status_code == 200 and meta_res.json().get('isSolid'):
                is_solid = 1
        except Exception as e:
            print("Error metadata:", e)

        try:
            block_res = requests.get(f"{HORNET_URL}/api/core/v2/blocks/{block_id}")
            if block_res.status_code == 200:
                is_valid = 1
        except Exception as e:
            print("Error bloque:", e)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO messages (block_id, tag, content, timestamp, is_solid, is_valid)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (block_id, tag, content, timestamp, is_solid, is_valid))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

    return jsonify({
        "status": "success",
        "block_id": block_id,
        "is_solid": bool(is_solid),
        "is_valid": bool(is_valid)
    }), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    tag = request.args.get('tag')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if tag:
        cursor.execute("SELECT * FROM messages WHERE tag = ?", (tag,))
    else:
        cursor.execute("SELECT * FROM messages")
        
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "block_id": r[1],
            "tag": r[2],
            "content": r[3],
            "timestamp": r[4],
            "is_solid": bool(r[5]),
            "is_valid": bool(r[6])
        })
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
