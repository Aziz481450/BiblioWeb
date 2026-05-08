import os
import sqlite3
from flask import Flask, request, jsonify, render_template
import database as db
import chatbot as chat

app = Flask(__name__)

# Lire la clé API depuis les variables d'environnement
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Initialisation de la base de données
db.init_db()

# ------------------ API Livres ------------------
@app.route('/api/livres', methods=['GET'])
def get_livres():
    livres = db.get_tous_livres()
    return jsonify([{
        'id': l[0], 'titre': l[1], 'auteur': l[2],
        'categorie': l[3], 'annee': l[4], 'quantite': l[5], 'statut': l[6]
    } for l in livres])

@app.route('/api/livres', methods=['POST'])
def add_livre():
    data = request.json
    db.ajouter_livre(
        data['titre'], data['auteur'],
        data.get('categorie', ''), data.get('annee', 0),
        data.get('quantite', 1), data.get('statut', 'disponible')
    )
    return '', 201

@app.route('/api/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    data = request.json
    db.modifier_livre(
        id, data['titre'], data['auteur'],
        data.get('categorie', ''), data.get('annee', 0),
        data.get('quantite', 1), data.get('statut', 'disponible')
    )
    return '', 200

@app.route('/api/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    db.supprimer_livre(id)
    return '', 200

@app.route('/api/recherche', methods=['GET'])
def search_livres():
    q = request.args.get('q', '')
    livres = db.rechercher_livres(q) if q else db.get_tous_livres()
    return jsonify([{
        'id': l[0], 'titre': l[1], 'auteur': l[2],
        'categorie': l[3], 'annee': l[4], 'quantite': l[5], 'statut': l[6]
    } for l in livres])

# ------------------ Chatbot ------------------
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    question = request.json.get('question', '')
    reponse = chat.ask_chatbot(question, GEMINI_API_KEY)
    return jsonify({'reponse': reponse})

# ------------------ Configuration API ------------------
@app.route('/api/config', methods=['POST'])
def set_api_key():
    global GEMINI_API_KEY
    new_key = request.json.get('api_key', '')
    if new_key:
        GEMINI_API_KEY = new_key
        return jsonify({'message': 'Clé mise à jour (en mémoire)'})
    return jsonify({'error': 'Clé invalide'}), 400

@app.route('/api/config', methods=['GET'])
def get_api_status():
    return jsonify({'has_key': bool(GEMINI_API_KEY)})

# ------------------ Page principale ------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------ Lancement ------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
