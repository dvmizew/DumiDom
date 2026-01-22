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
 
CREATE TABLE IF NOT EXISTS playlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  owner TEXT
);
 
CREATE TABLE IF NOT EXISTS playlist_tracks (
  playlist_id INTEGER NOT NULL,
  track_id INTEGER NOT NULL,
  position INTEGER,
  PRIMARY KEY (playlist_id, track_id),
  FOREIGN KEY (playlist_id) REFERENCES playlists(id),
  FOREIGN KEY (track_id) REFERENCES tracks(id)
);
 
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  album_id INTEGER NOT NULL,
  reviewer TEXT NOT NULL,
  rating INTEGER CHECK(rating >= 1 AND rating <= 5),
  comment TEXT,
  FOREIGN KEY (album_id) REFERENCES albums(id)
);
"""
 
DATA_SQL = """
-- Artists
INSERT INTO artists(name) VALUES
  ('The Example Band'),
  ('Demo Artist'),
  ('Sample Singer'),
  ('No Album Artist'),
  ('Multi Genre Artist'),
  ('Duplicate Name'),
  ('Duplicate Name'),
  ('Jazz Quartet'),
  ('Pop Star'),
  ('Rockers'),
  ('Indie Group'),
  ('Electronic Duo'),
  ('Folk Singer'),
  ('HipHop Crew'),
  ('Classical Ensemble'),
  ('Experimentalist'),
  ('Cover Band'),
  ('One Hit Wonder'),
  ('Obscure Artist'),
  ('Legendary Band');

-- Albums
INSERT INTO albums(artist_id, title, year) VALUES
  (1, 'First Album', 2010),
  (1, 'Second Album', 2012),
  (2, 'Anthology', 2018),
  (3, 'Solo Debut', 2020),
  (5, 'Genre Fusion', 2021),
  (5, 'Rock Only', 2022),
  (6, 'Unique Album', 2015),
  (8, 'Jazzed Up', 2011),
  (9, 'Pop Explosion', 2013),
  (10, 'Rock Revolution', 2014),
  (11, 'Indie Vibes', 2016),
  (12, 'Electric Dreams', 2017),
  (13, 'Folk Tales', 2019),
  (14, 'HipHop Hooray', 2020),
  (15, 'Classics Forever', 2015),
  (16, 'Sound Experiments', 2021),
  (17, 'Covers Vol.1', 2018),
  (18, 'The Only Hit', 2012),
  (19, 'Hidden Gems', 2014),
  (20, 'Legendary Hits', 2000);

-- Tracks
INSERT INTO tracks(album_id, name, duration, genre) VALUES
  (1, 'Intro', 120, 'Rock'),
  (1, 'Fire', 210, 'Rock'),
  (1, 'Water', 200, 'Rock'),
  (2, 'Sky', 240, 'Pop'),
  (2, 'Earth', 220, 'Pop'),
  (3, 'Memory Lane', 300, 'Indie'),
  (3, 'Sunrise', 260, 'Indie'),
  (4, 'Alone', 190, 'Acoustic'),
  (5, 'Fusion Start', 180, 'Jazz'),
  (5, 'Fusion End', 210, 'Rock'),
  (6, 'Rock Anthem', 250, 'Rock'),
  (7, 'Unique Song', 230, 'Pop'),
  (2, 'Sky', 245, 'Pop'),
  (3, 'Sunrise', 260, 'Indie'),
  (8, 'Quartet Jam', 300, 'Jazz'),
  (8, 'Blue Note', 220, 'Jazz'),
  (9, 'Pop Hit', 210, 'Pop'),
  (9, 'Dance Floor', 200, 'Pop'),
  (10, 'Rock On', 240, 'Rock'),
  (10, 'Ballad', 260, 'Rock'),
  (11, 'Indie Start', 180, 'Indie'),
  (11, 'Indie End', 210, 'Indie'),
  (12, 'Electric Shock', 220, 'Electronic'),
  (12, 'Dreamscape', 230, 'Electronic'),
  (13, 'Folk Song', 200, 'Folk'),
  (13, 'Campfire', 180, 'Folk'),
  (14, 'Rap Battle', 210, 'HipHop'),
  (14, 'Crew Anthem', 220, 'HipHop'),
  (15, 'Symphony', 400, 'Classical'),
  (15, 'Concerto', 380, 'Classical'),
  (16, 'Noise', 100, 'Experimental'),
  (16, 'Silence', 10, 'Experimental'),
  (17, 'Cover 1', 210, 'Rock'),
  (17, 'Cover 2', 220, 'Pop'),
  (18, 'The Hit', 180, 'Pop'),
  (19, 'Hidden Track', 190, 'Indie'),
  (20, 'Legendary Song', 300, 'Rock');

-- Playlists
INSERT INTO playlists(name, owner) VALUES
  ('Workout Mix', 'Alice'),
  ('Chill Vibes', 'Bob'),
  ('Indie Only', 'Carol'),
  ('Empty Playlist', 'Nobody'),
  ('Jazz Collection', 'Eve'),
  ('Pop Party', 'Frank'),
  ('Rock Marathon', 'Grace'),
  ('Classical Moments', 'Heidi'),
  ('Experimental Set', 'Ivan'),
  ('Covers Only', 'Judy');

-- Playlist Tracks
INSERT INTO playlist_tracks(playlist_id, track_id, position) VALUES
  (1, 1, 1), (1, 2, 2), (1, 4, 3), (1, 10, 4), (1, 20, 5),
  (2, 3, 1), (2, 5, 2), (2, 8, 3), (2, 17, 4), (2, 18, 5),
  (3, 6, 1), (3, 7, 2), (3, 14, 3), (3, 19, 4),
  (5, 15, 1), (5, 16, 2),
  (6, 17, 1), (6, 18, 2),
  (7, 9, 1), (7, 10, 2), (7, 20, 3),
  (8, 15, 1), (8, 16, 2),
  (9, 31, 1), (9, 32, 2),
  (10, 33, 1), (10, 34, 2);

-- Reviews
INSERT INTO reviews(album_id, reviewer, rating, comment) VALUES
  (1, 'Alice', 5, 'Great album!'),
  (2, 'Bob', 4, 'Solid follow-up.'),
  (3, 'Carol', 3, 'Nice compilation.'),
  (4, 'Dave', 5, 'Amazing debut!'),
  (5, 'Eve', 2, 'Not my style.'),
  (6, 'Frank', 4, 'Good rock album.'),
  (7, 'Grace', 5, 'Unique!'),
  (8, 'Heidi', 1, 'Did not like it.'),
  (9, 'Ivan', 3, 'Average.'),
  (10, 'Judy', 4, 'Pretty good.'),
  (11, 'Mallory', 5, 'Genre mix is awesome!'),
  (12, 'Oscar', 2, 'Too electronic.'),
  (13, 'Peggy', 5, 'Folk at its best.'),
  (14, 'Sybil', 3, 'Fun hiphop.'),
  (15, 'Trent', 5, 'Classical masterpiece.'),
  (16, 'Victor', 1, 'Too weird.'),
  (17, 'Walter', 4, 'Nice covers.'),
  (18, 'Yvonne', 5, 'One hit wonder!'),
  (19, 'Zara', 2, 'Obscure but interesting.'),
  (20, 'Xander', 5, 'Legendary!');
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