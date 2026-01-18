import os
import sqlite3

DB_PATH = os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS artists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS albums (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artist_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  year INTEGER,
  FOREIGN KEY (artist_id) REFERENCES artists(id)
);

CREATE TABLE IF NOT EXISTS tracks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  album_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  duration INTEGER,
  genre TEXT,
  FOREIGN KEY (album_id) REFERENCES albums(id)
);
"""

DATA_SQL = """
INSERT INTO artists(name) VALUES
  ('The Example Band'),
  ('Demo Artist'),
  ('Sample Singer');

INSERT INTO albums(artist_id, title, year) VALUES
  (1, 'First Album', 2010),
  (1, 'Second Album', 2012),
  (2, 'Anthology', 2018),
  (3, 'Solo Debut', 2020);

INSERT INTO tracks(album_id, name, duration, genre) VALUES
  (1, 'Intro', 120, 'Rock'),
  (1, 'Fire', 210, 'Rock'),
  (1, 'Water', 200, 'Rock'),
  (2, 'Sky', 240, 'Pop'),
  (2, 'Earth', 220, 'Pop'),
  (3, 'Memory Lane', 300, 'Indie'),
  (3, 'Sunrise', 260, 'Indie'),
  (4, 'Alone', 190, 'Acoustic');
"""

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.executescript(SCHEMA_SQL)
        cur.executescript(DATA_SQL)
        conn.commit()
    print(f"Initialized demo DB at {DB_PATH}")

if __name__ == "__main__":
    main()