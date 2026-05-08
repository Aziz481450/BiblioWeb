import re
import sqlite3
import requests
import database as db

# Cache du modèle disponible (pour ne pas interroger à chaque fois)
_available_model = None

def get_available_model(api_key):
    """Interroge l'API pour obtenir le premier modèle supportant generateContent."""
    global _available_model
    if _available_model:
        return _available_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        data = r.json()
        for model in data.get("models", []):
            if "generateContent" in model.get("supportedGenerationMethods", []):
                model_name = model["name"].split("/")[-1]  # extraire "gemini-1.5-flash"
                _available_model = model_name
                return model_name
        return None
    except Exception:
        return None

def reponse_locale(question):
    """Fallback utilisant des mots-clés (quand l'API n'est pas disponible)."""
    q = question.lower()
    conn = sqlite3.connect(db.DB_PATH)
    cur = conn.cursor()
    # ID
    m = re.search(r'id\s*(\d+)', q)
    if m:
        row = cur.execute("SELECT id, titre, auteur, statut FROM livres WHERE id=?", (m.group(1),)).fetchone()
        conn.close()
        if row:
            return f"📖 #{row[0]} – {row[1]} par {row[2]} – Statut : {row[3]}"
        return "Aucun livre avec cet ID."
    # Disponibles
    if 'disponible' in q:
        rows = cur.execute("SELECT id, titre, auteur FROM livres WHERE statut='disponible'").fetchall()
        conn.close()
        if rows:
            return "Livres disponibles : " + ", ".join(f"#{r[0]} {r[1]} ({r[2]})" for r in rows)
        return "Aucun livre disponible."
    # Auteur
    m_auteur = re.search(r'(?:de|par)\s+([a-zéèêëçàùâûîôäöüß\s\-]+)', q)
    if m_auteur:
        auteur = m_auteur.group(1).strip().title()
        rows = cur.execute("SELECT id, titre, statut FROM livres WHERE auteur LIKE ?", (f"%{auteur}%",)).fetchall()
        conn.close()
        if rows:
            return f"Livres de {auteur} : " + ", ".join(f"#{r[0]} {r[1]} ({r[2]})" for r in rows)
        return f"Aucun livre trouvé pour {auteur}."
    conn.close()
    return "Je ne comprends pas. Essayez : 'livres disponibles', 'livre id 3', 'livres de Victor Hugo'."

def chat(question, api_key=""):
    if not api_key:
        return "⚠️ [Mode LOCAL – Aucune clé API fournie]\n" + reponse_locale(question)

    # Détection du modèle disponible
    model_name = get_available_model(api_key)
    if not model_name:
        return "⚠️ [Mode LOCAL – Impossible de contacter l'API Gemini (aucun modèle trouvé)]\n" + reponse_locale(question)

    # Construction de l'URL avec le modèle dynamique
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    prompt = f"""Tu es un assistant de bibliothèque expert. Réponds en français, de manière précise et amicale.
Voici la question posée par l'utilisateur : {question}
Si la question concerne les livres présents dans la base de données, utilise les informations suivantes (issues de SQLite) :
{get_contexte_bibliotheque()}
Réponds de façon naturelle, sans inventer de données."""
    
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            reponse_ia = data["candidates"][0]["content"]["parts"][0]["text"]
            return f"🧠 [Gemini – {model_name}] {reponse_ia}"
        else:
            # Erreur HTTP (clé invalide, quota, etc.)
            return f"⚠️ [Mode LOCAL – API erreur {r.status_code}] {reponse_locale(question)}"
    except Exception as e:
        return f"⚠️ [Mode LOCAL – Connexion échouée] {reponse_locale(question)}"

def get_contexte_bibliotheque():
    """Récupère un résumé des livres pour guider l'IA."""
    conn = sqlite3.connect(db.DB_PATH)
    cur = conn.cursor()
    livres = cur.execute("SELECT titre, auteur, statut FROM livres LIMIT 5").fetchall()
    conn.close()
    if livres:
        return "Exemples de livres : " + ", ".join(f"'{l[0]}' de {l[1]} ({l[2]})" for l in livres)
    return "Aucun livre en base."