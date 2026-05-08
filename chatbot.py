import re
import sqlite3
import requests
import database as db

def reponse_locale(question):
    q = question.lower()
    conn = sqlite3.connect(db.DB_NAME)
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

def ask_chatbot(question, api_key):
    if not api_key:
        return "[Mode local] " + reponse_locale(question)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Réponds en français à cette question sur une bibliothèque : {question}. Sois concis."
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=8)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "[Mode local (API erreur)] " + reponse_locale(question)
    except:
        return "[Mode local (connexion)] " + reponse_locale(question)
