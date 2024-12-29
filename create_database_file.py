import sqlite3

# Tastatur-Tasten und Befehle, die in die Datenbank eingefügt werden
def create_database():
    # Verbindet sich mit der Datenbank (wird erstellt, wenn sie nicht existiert)
    conn = sqlite3.connect("keyboard_data.db")
    cursor = conn.cursor()

    # Erstellen einer Tabelle für Tastatur-Tasten
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT
    )
    ''')

    # Daten für Text-Eingabe-Tasten und Steuerungstasten (Automatisch erstellte Liste)
    keys_data = [
        # Text-Eingabetasten (Buchstaben und wichtige Tasten)
        ("A", "Key", "Der Buchstabe A"),
        ("B", "Key", "Der Buchstabe B"),
        ("C", "Key", "Der Buchstabe C"),
        ("D", "Key", "Der Buchstabe D"),
        ("E", "Key", "Der Buchstabe E"),
        ("F", "Key", "Der Buchstabe F"),
        ("G", "Key", "Der Buchstabe G"),
        ("H", "Key", "Der Buchstabe H"),
        ("I", "Key", "Der Buchstabe I"),
        ("J", "Key", "Der Buchstabe J"),
        ("K", "Key", "Der Buchstabe K"),
        ("L", "Key", "Der Buchstabe L"),
        ("M", "Key", "Der Buchstabe M"),
        ("N", "Key", "Der Buchstabe N"),
        ("O", "Key", "Der Buchstabe O"),
        ("P", "Key", "Der Buchstabe P"),
        ("Q", "Key", "Der Buchstabe Q"),
        ("R", "Key", "Der Buchstabe R"),
        ("S", "Key", "Der Buchstabe S"),
        ("T", "Key", "Der Buchstabe T"),
        ("U", "Key", "Der Buchstabe U"),
        ("V", "Key", "Der Buchstabe V"),
        ("W", "Key", "Der Buchstabe W"),
        ("X", "Key", "Der Buchstabe X"),
        ("Y", "Key", "Der Buchstabe Y"),
        ("Z", "Key", "Der Buchstabe Z"),
        ("1", "Key", "Die Zahl 1"),
        ("2", "Key", "Die Zahl 2"),
        ("3", "Key", "Die Zahl 3"),
        ("4", "Key", "Die Zahl 4"),
        ("5", "Key", "Die Zahl 5"),
        ("6", "Key", "Die Zahl 6"),
        ("7", "Key", "Die Zahl 7"),
        ("8", "Key", "Die Zahl 8"),
        ("9", "Key", "Die Zahl 9"),
        ("0", "Key", "Die Zahl 0"),
        ("Space", "Key", "Setzt einen Leerraum ein."),
        ("Enter", "Key", "Bestätigt die Eingabe."),
        
        # Steuerungstasten
        ("Ctrl", "ControlKey", "Wird in Kombination mit anderen Tasten verwendet."),
        ("Alt", "ControlKey", "Wird in Kombination mit anderen Tasten verwendet."),
        ("Shift", "ControlKey", "Ermöglicht Großbuchstaben oder Sonderzeichen."),
        ("Esc", "ControlKey", "Abbricht eine Aktion oder schließt ein Fenster."),
        
        # Tastenkombinationen
        ("Ctrl + C", "KeyCombination", "Kopiert den markierten Text."),
        ("Ctrl + V", "KeyCombination", "Fügt den kopierten Text ein."),
        ("Ctrl + X", "KeyCombination", "Schneidet den markierten Text aus."),
        ("Ctrl + Z", "KeyCombination", "Macht die letzte Aktion rückgängig."),
        ("Ctrl + A", "KeyCombination", "Wählt den gesamten Text aus."),
        ("Ctrl + S", "KeyCombination", "Speichert die aktuelle Datei."),
        ("Alt + Tab", "KeyCombination", "Wechselt zwischen offenen Programmen."),

        ("Text", "Text", "Text den man schreibt z.B. Hello World"),
        ("Wait", "Action", "Wartet eine Bestimmte Zeit")
    ]

    # Einfügen der Tastatur-Daten in die Tabelle
    cursor.executemany('''
    INSERT INTO keys (name, type, description) VALUES (?, ?, ?)
    ''', keys_data)

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

# Daten aus der Datenbank abrufen
def fetch_keys():
    # Verbindet sich mit der Datenbank
    conn = sqlite3.connect("keyboard_data.db")
    cursor = conn.cursor()

    # Abrufen aller Tasten aus der Datenbank, nach Typ sortiert
    cursor.execute('''
    SELECT name, type, description FROM keys ORDER BY type, name
    ''')

    keys = cursor.fetchall()

    # Ausgabe der Daten
    for key in keys:
        print(f"Name: {key[0]}, Typ: {key[1]}, Beschreibung: {key[2]}")

    # Verbindung schließen
    conn.close()

if __name__ == "__main__":
    # Erstellen und Füllen der Datenbank
    create_database()

    # Daten aus der Datenbank anzeigen
    fetch_keys()
