import sqlite3 as db
from ssl import VERIFY_ALLOW_PROXY_CERTS


def createDB():
    conn = db.connect("players.db")
    conn.commit()
    conn.close()

def createTable(nombreTabla):
    conn = db.connect("players.db")
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {nombreTabla}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE CHECK(length(name) <= 12),
        money INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
        )"""
    )
    conn.commit()
    conn.close()


    #------------AGREGA EL NOMBRE DEL JUGADOR A LA LISTA DE JUGADORES---------------------
def insertrow(nombreTabla, name):
    conn = db.connect("players.db")
    cursor = conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO {nombreTabla} (name)
        VALUES (?)
        """,
        (name,)
    )

    conn.commit()
    conn.close()


def editnameplayer(id, newname):
    conn = db.connect("players.db")
    cursor = conn.cursor()
    conn.execute(
        f"""
            UPDATE player
            SET name = ?
            WHERE id = ?
        """,
        (newname, id)
    )
    conn.commit()
    conn.close
#-------------BORRA UNA TABLA DE LA BASE DE DATOS-------------
def deletetable(nombreTabla):
    conn = db.connect("players.db")
    cursor = conn.cursor()
    conn.execute(
        f"""
        DROP TABLE {nombreTabla};"""
    )
    conn.commit()
    conn.close()
#-----------ELIMINAR CUENTA DE JUGADOR-----------------
def deleteplayer(id, playername):
    conn = db.connect("players.db")
    cursor = conn.cursor()
    conn.execute(
        f"""
        DELETE FROM player WHERE id == {id} AND name == '{playername}'"""
    )
    conn.commit()
    conn.close()




if __name__ == "__main__":
    #createDB()
    #deletetable("player")
    #createTable("player")
    #insertrow("player", "Daniel")
    #deleteplayer(1, "Daniel")
    editnameplayer(1, "Terrible_1pqipwdiasd2")