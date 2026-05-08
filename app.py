from flask import Flask, request, jsonify, render_template
import database as db
import chatbot as cb

app = Flask(__name__)

# Stockage simple de la clé (en mémoire)
API_KEY = ""

@app.route('/')
def home():
    return render_template('index.html')

# --- API Livres ---
@app.route('/api/livres', methods=['GET'])
def get_livres():
    livres = db.get_all()
    return jsonify([{
        'id': l[0], 'titre': l[1], 'auteur': l[2],
        'categorie': l[3], 'annee': l[4], 'quantite': l[5], 'statut': l[6]
    } for l in livres])

@app.route('/api/livres', methods=['POST'])
def add_livre():
    data = request.json
    db.add(data['titre'], data['auteur'], data.get('categorie', ''),
           data.get('annee', 0), data.get('quantite', 1), data.get('statut', 'disponible'))
    return '', 201

@app.route('/api/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    data = request.json
    db.update(id, data['titre'], data['auteur'], data.get('categorie', ''),
              data.get('annee', 0), data.get('quantite', 1), data.get('statut', 'disponible'))
    return '', 200

@app.route('/api/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    db.delete(id)
    return '', 200

@app.route('/api/recherche', methods=['GET'])
def search_livres():
    q = request.args.get('q', '')
    livres = db.search(q) if q else db.get_all()
    return jsonify([{
        'id': l[0], 'titre': l[1], 'auteur': l[2],
        'categorie': l[3], 'annee': l[4], 'quantite': l[5], 'statut': l[6]
    } for l in livres])

# --- API Chatbot ---
@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.json.get('question', '')
    reponse = cb.chat(question, API_KEY)
    return jsonify({'reponse': reponse})

# --- API Configuration (clé Gemini) ---
@app.route('/api/config', methods=['POST'])
def set_key():
    global API_KEY
    API_KEY = request.json.get('api_key', '')
    return '', 200

@app.route('/api/config', methods=['GET'])
def get_key_status():
    return jsonify({'has_key': bool(API_KEY)})

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)