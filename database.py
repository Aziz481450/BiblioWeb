import sqlite3

DB_PATH = "bibliotheque.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                categorie TEXT,
                annee INTEGER,
                quantite INTEGER DEFAULT 1,
                statut TEXT DEFAULT 'disponible'
            )
        ''')
        cur = conn.execute("SELECT COUNT(*) FROM livres")
        if cur.fetchone()[0] == 0:
            exemples = [
                ("Les Misérables", "Victor Hugo", "Roman", 1862, 3, "disponible"),
                ("1984", "George Orwell", "Science", 1949, 2, "emprunté"),
                ("Le Petit Prince", "Antoine de Saint-Exupéry", "Roman", 1943, 5, "disponible"),
                ("Sapiens", "Yuval Noah Harari", "Histoire", 2011, 1, "réservé"),
                ("Clean Code", "Robert C. Martin", "Informatique", 2008, 2, "disponible"),
            ]
            conn.executemany(
                "INSERT INTO livres(titre, auteur, categorie, annee, quantite, statut) VALUES (?,?,?,?,?,?)",
                exemples
            )

def get_all():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres ORDER BY id").fetchall()

def add(titre, auteur, categorie, annee, quantite, statut):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO livres(titre, auteur, categorie, annee, quantite, statut) VALUES (?,?,?,?,?,?)",
                     (titre, auteur, categorie, int(annee), int(quantite), statut))

def update(id, titre, auteur, categorie, annee, quantite, statut):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE livres SET titre=?, auteur=?, categorie=?, annee=?, quantite=?, statut=? WHERE id=?",
                     (titre, auteur, categorie, int(annee), int(quantite), statut, id))

def delete(id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM livres WHERE id=?", (id,))

def search(keyword):
    with sqlite3.connect(DB_PATH) as conn:
        if keyword.isdigit():
            return conn.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE id=? OR titre LIKE ? OR auteur LIKE ?",
                                (int(keyword), f"%{keyword}%", f"%{keyword}%")).fetchall()
        else:
            return conn.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE titre LIKE ? OR auteur LIKE ?",
                                (f"%{keyword}%", f"%{keyword}%")).fetchall()