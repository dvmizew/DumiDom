from .base import Provider
import re

class NaiveProvider(Provider):
    name = "naive"

    def generate_sql(self, question, schema_context):
        """
        Generate SQL using simple pattern matching, but use schema_context to adapt to table/column names.
        """
        q = question.lower()
        # Parse schema_context for table/column names
        tables = {}
        for line in schema_context.splitlines():
            if line.startswith('TABLE '):
                current = line.split()[1]
                tables[current] = []
            elif line.strip().startswith('--') or not line.strip():
                continue
            elif line.strip().startswith('FOREIGN KEY'):
                continue
            elif line.startswith('  ') and ' ' in line.strip():
                col = line.strip().split()[0]
                if current:
                    tables[current].append(col)

        # Helper to get first table/column by partial name
        def find_table(name):
            for t in tables:
                if name in t:
                    return t
            return None
        def find_col(table, name):
            for c in tables.get(table, []):
                if name in c:
                    return c
            return None

        # Patterns
        if "how many" in q and ("tracks" in q or "songs" in q):
            t = find_table("track") or "tracks"
            return f"SELECT COUNT(*) FROM {t};"
        if "how many" in q and "albums" in q:
            t = find_table("album") or "albums"
            return f"SELECT COUNT(*) FROM {t};"
        m = re.search(r"tracks by (artist|band) (.+)", q)
        if m:
            artist = m.group(2).strip(' "\'')
            t_tracks = find_table("track") or "tracks"
            t_albums = find_table("album") or "albums"
            t_artists = find_table("artist") or "artists"
            c_name = find_col(t_tracks, "name") or "name"
            c_title = find_col(t_albums, "title") or "title"
            c_artist_name = find_col(t_artists, "name") or "name"
            c_album_id = find_col(t_tracks, "album_id") or "album_id"
            c_artist_id = find_col(t_albums, "artist_id") or "artist_id"
            return (
                f"SELECT {t_tracks}.{c_name}, {t_albums}.{c_title} FROM {t_tracks} "
                f"JOIN {t_albums} ON {t_tracks}.{c_album_id} = {t_albums}.id "
                f"JOIN {t_artists} ON {t_albums}.{c_artist_id} = {t_artists}.id "
                f"WHERE {t_artists}.{c_artist_name} LIKE '%{artist}%';"
            )
        if "top" in q and "albums" in q and ("track" in q or "songs" in q):
            t_albums = find_table("album") or "albums"
            t_artists = find_table("artist") or "artists"
            t_tracks = find_table("track") or "tracks"
            c_title = find_col(t_albums, "title") or "title"
            c_artist_name = find_col(t_artists, "name") or "name"
            c_album_id = find_col(t_tracks, "album_id") or "album_id"
            c_artist_id = find_col(t_albums, "artist_id") or "artist_id"
            c_track_id = find_col(t_tracks, "id") or "id"
            return (
                f"SELECT {t_albums}.{c_title}, {t_artists}.{c_artist_name}, COUNT({t_tracks}.{c_track_id}) AS track_count "
                f"FROM {t_albums} JOIN {t_artists} ON {t_albums}.{c_artist_id} = {t_artists}.id "
                f"LEFT JOIN {t_tracks} ON {t_tracks}.{c_album_id} = {t_albums}.id "
                f"GROUP BY {t_albums}.id ORDER BY track_count DESC LIMIT 5;"
            )
        t_artists = find_table("artist") or "artists"
        c_name = find_col(t_artists, "name") or "name"
        return f"SELECT {c_name} FROM {t_artists} LIMIT 5;"

    def summarize(self, question, rows):
        q = question.lower()
        if "count" in q or "how many" in q:
            if rows and len(rows[0]) >= 1:
                return f"Found {rows[0][0]} items"
        if "top" in q:
            return "Top items: " + ", ".join(f"{r[0]}" for r in rows)
        return f"Found {len(rows)} results"
