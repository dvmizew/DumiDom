from .base import Provider
import re

class NaiveProvider(Provider):
    name = "naive"

    def generate_sql(self, question, schema_context):
        q = question.lower()
        if "how many" in q and ("tracks" in q or "songs" in q):
            return "SELECT COUNT(*) FROM tracks;"
        if "how many" in q and "albums" in q:
            return "SELECT COUNT(*) FROM albums;"
        m = re.search(r"tracks by (artist|band) (.+)", q)
        if m:
            artist = m.group(2).strip(' "\'')
            return (
                "SELECT tracks.name, albums.title FROM tracks "
                "JOIN albums ON tracks.album_id = albums.id "
                "JOIN artists ON albums.artist_id = artists.id "
                f"WHERE artists.name LIKE '%{artist}%';"
            )
        if "top" in q and "albums" in q and ("track" in q or "songs" in q):
            return (
                "SELECT albums.title, artists.name, COUNT(tracks.id) AS track_count "
                "FROM albums JOIN artists ON albums.artist_id = artists.id "
                "LEFT JOIN tracks ON tracks.album_id = albums.id "
                "GROUP BY albums.id ORDER BY track_count DESC LIMIT 5;"
            )
        return "SELECT name FROM artists LIMIT 5;"

    def summarize(self, question, rows):
        q = question.lower()
        if "count" in q or "how many" in q:
            if rows and len(rows[0]) >= 1:
                return f"Found {rows[0][0]} items"
        if "top" in q:
            return "Top items: " + ", ".join(f"{r[0]}" for r in rows)
        return f"Found {len(rows)} results"
