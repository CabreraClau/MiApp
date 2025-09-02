import os
import json
import datetime
from flask import Flask, jsonify

# Config: carpeta donde se guardan las notas (por defecto ./data)
NOTES_DIR = os.environ.get("NOTES_DIR", "./data")
NOTES_FILE = os.path.join(NOTES_DIR, "notes.ndjson")

# Asegurarse que exista la carpeta
os.makedirs(NOTES_DIR, exist_ok=True)

app = Flask(__name__)

def add_note_to_file(text: str):
    """Agrega una nota como una línea JSON en NOTES_FILE (NDJSON)."""
    entry = {
        "note": text,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    # Append en formato NDJSON (una línea JSON por nota)
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def read_all_notes():
    """Lee todas las notas desde NOTES_FILE y devuelve lista de objetos."""
    if not os.path.exists(NOTES_FILE):
        return []
    notes = []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                notes.append(json.loads(line))
            except json.JSONDecodeError:
                # Ignorar líneas corruptas
                continue
    return notes

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "message": "API de notas activo"})

# Endpoint según tu especificación: /add/{note}
# Uso: /add/Esto%20es%20una%20nota  (note => URL-encoded)
@app.route("/add/<path:note>", methods=["GET", "POST"])
def add_note_endpoint(note):
    # note viene URL-decodificado automáticamente por Flask
    add_note_to_file(note)
    return jsonify({"status": "ok", "note": note})

@app.route("/list", methods=["GET"])
def list_notes_endpoint():
    notes = read_all_notes()
    return jsonify(notes)

if __name__ == "__main__":
    # Host 0.0.0.0 para que sea accesible desde fuera si lo corrés en un contenedor
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
