import sqlite3

DB_NAME = "bibliotheque.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
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
    cursor.execute("SELECT COUNT(*) FROM livres")
    if cursor.fetchone()[0] == 0:
        exemples = [
            ("Les Misérables", "Victor Hugo", "Roman", 1862, 3, "disponible"),
            ("1984", "George Orwell", "Science", 1949, 2, "emprunté"),
            ("Le Petit Prince", "Saint-Exupéry", "Roman", 1943, 5, "disponible"),
            ("Sapiens", "Harari", "Histoire", 2011, 1, "réservé"),
            ("Clean Code", "Robert Martin", "Informatique", 2008, 2, "disponible"),
        ]
        cursor.executemany(
            "INSERT INTO livres(titre, auteur, categorie, annee, quantite, statut) VALUES (?,?,?,?,?,?)",
            exemples
        )
    conn.commit()
    conn.close()

def get_tous_livres():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres ORDER BY id")
    data = cursor.fetchall()
    conn.close()
    return data

def ajouter_livre(titre, auteur, categorie, annee, quantite, statut):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livres (titre, auteur, categorie, annee, quantite, statut) VALUES (?,?,?,?,?,?)",
                   (titre, auteur, categorie, annee, quantite, statut))
    conn.commit()
    conn.close()

def modifier_livre(id, titre, auteur, categorie, annee, quantite, statut):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE livres SET titre=?, auteur=?, categorie=?, annee=?, quantite=?, statut=? WHERE id=?",
                   (titre, auteur, categorie, annee, quantite, statut, id))
    conn.commit()
    conn.close()

def supprimer_livre(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livres WHERE id=?", (id,))
    conn.commit()
    conn.close()

def rechercher_livres(mot_cle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if mot_cle.isdigit():
        cursor.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE id=? OR titre LIKE ? OR auteur LIKE ?",
                       (int(mot_cle), f"%{mot_cle}%", f"%{mot_cle}%"))
    else:
        cursor.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE titre LIKE ? OR auteur LIKE ?",
                       (f"%{mot_cle}%", f"%{mot_cle}%"))
    data = cursor.fetchall()
    conn.close()
    return data
