class Provider:
    name = "base"

    def generate_sql(self, question, schema_context):
        raise NotImplementedError

    def summarize(self, question, rows):
        return f"Found {len(rows)} results"
