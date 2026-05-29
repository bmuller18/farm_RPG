import sqlite3 as db


def createDB():
    conn = db.connect("players.db")
    conn.commit()
    conn.close()

def createTable():
    conn = db.connect("players.db")
    cursor = conn.cursor()
    conn.execute(
        """CREATE TABLE player(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        money INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
        )"""
    )
    conn.commit()
    conn.close()



if __name__ == "__main__":
    #createDB()
    createTable()