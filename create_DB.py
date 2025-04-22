import sqlite3

conn = sqlite3.connect("mainDB.db")
cur = conn.cursor() 

cur.execute('''
    CREATE TABLE game (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT NOT NULL,
        original_price REAL NOT NULL,
        discount_price REAL NOT NULL,
        discount_startdate TEXT,
        discount_enddate TEXT,
        genre TEXT,
        release_date TEXT,
        maker TEXT,
        player_number TEXT,
        product_type TEXT,
        game_language TEXT,
        game_image_url TEXT,
        game_url TEXT,
        collect_date TEXT,
        UNIQUE(game_name, product_type)
        )
    ''')
            
conn.commit()
conn.close()